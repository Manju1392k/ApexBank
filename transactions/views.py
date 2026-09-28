from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from accounts.models import BankAccount
from .models import Transaction
from .forms import WithdrawalForm, TransferForm, AdminDepositForm
from decimal import Decimal

def is_admin_or_staff(user):
    """Helper test to verify user is admin or staff member."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
def dashboard_view(request):
    """
    Customer Dashboard:
    Displays balance, quick stats, and recent 5 transactions.
    If an admin logs in and visits dashboard, they are directed to the admin portal.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        bank_account = request.user.bank_account
    except BankAccount.DoesNotExist:
        messages.error(request, "Bank account profile not initialized. Contact administration.")
        return redirect('logout')

    # Fetch recent transactions
    recent_transactions = Transaction.objects.filter(
        Q(sender_account=bank_account) | Q(receiver_account=bank_account)
    ).select_related('sender_account', 'receiver_account').order_by('-timestamp')[:5]

    context = {
        'account': bank_account,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'transactions/dashboard.html', context)


@login_required
def withdraw_view(request):
    """
    Enables authenticated customer to safely withdraw funds from their account.
    Row-level locking (`select_for_update`) prevents concurrency issues.
    """
    if request.user.is_staff:
        messages.warning(request, "Staff members cannot execute customer withdrawals from this portal.")
        return redirect('admin_dashboard')

    account = request.user.bank_account

    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            desc = form.cleaned_data.get('description', '') or 'ATM / Self Withdrawal'

            try:
                with transaction.atomic():
                    # Lock the specific bank account row
                    locked_account = BankAccount.objects.select_for_update().get(pk=account.pk)

                    if locked_account.balance < amount:
                        messages.error(
                            request, 
                            f"Insufficient balance! Your current balance is ₹{locked_account.balance}."
                        )
                        return render(request, 'transactions/withdraw.html', {'form': form, 'account': locked_account})

                    # Deduct funds
                    locked_account.balance -= amount
                    locked_account.save()

                    # Create Transaction record
                    txn = Transaction.objects.create(
                        transaction_type='WITHDRAWAL',
                        sender_account=locked_account,
                        receiver_account=None,
                        amount=amount,
                        status='SUCCESS',
                        description=desc,
                        initiated_by=request.user
                    )

                messages.success(
                    request, 
                    f"Successfully withdrawn ₹{amount:,.2f}. Transaction Ref: {txn.reference_id}. New Balance: ₹{locked_account.balance:,.2f}"
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Withdrawal could not be completed: {str(e)}")
    else:
        form = WithdrawalForm()

    return render(request, 'transactions/withdraw.html', {'form': form, 'account': account})


@login_required
def transfer_view(request):
    """
    Peer-to-peer transfer between registered accounts.
    Executes atomically with row locking in ordered ID sequence to eliminate deadlocks.
    """
    if request.user.is_staff:
        messages.warning(request, "Staff members cannot execute customer transfers.")
        return redirect('admin_dashboard')

    sender_account = request.user.bank_account

    if request.method == 'POST':
        form = TransferForm(request.POST, sender_account=sender_account)
        if form.is_valid():
            recipient_acc_no = form.cleaned_data['recipient_account_number']
            amount = form.cleaned_data['amount']
            desc = form.cleaned_data.get('description', '') or f"Transfer to {recipient_acc_no}"

            try:
                with transaction.atomic():
                    # Fetch and lock both accounts ordered by PK to prevent DB deadlocks
                    acc_ids = sorted([sender_account.id, BankAccount.objects.get(account_number=recipient_acc_no).id])
                    locked_accounts = {
                        acc.id: acc for acc in BankAccount.objects.select_for_update().filter(id__in=acc_ids)
                    }

                    locked_sender = locked_accounts[sender_account.id]
                    recipient_target = BankAccount.objects.get(account_number=recipient_acc_no)
                    locked_receiver = locked_accounts[recipient_target.id]

                    if locked_sender.balance < amount:
                        messages.error(
                            request, 
                            f"Insufficient balance! Available balance is ₹{locked_sender.balance}."
                        )
                        return render(request, 'transactions/transfer.html', {'form': form, 'account': locked_sender})

                    # Perform transfer
                    locked_sender.balance -= amount
                    locked_receiver.balance += amount
                    locked_sender.save()
                    locked_receiver.save()

                    # Record transaction
                    txn = Transaction.objects.create(
                        transaction_type='TRANSFER',
                        sender_account=locked_sender,
                        receiver_account=locked_receiver,
                        amount=amount,
                        status='SUCCESS',
                        description=desc,
                        initiated_by=request.user
                    )

                messages.success(
                    request,
                    f"Successfully transferred ₹{amount:,.2f} to {locked_receiver.user.get_full_name() or locked_receiver.account_number}. Reference: {txn.reference_id}"
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Transfer failed: {str(e)}")
    else:
        form = TransferForm(sender_account=sender_account)

    return render(request, 'transactions/transfer.html', {'form': form, 'account': sender_account})


@login_required
def statement_view(request):
    """
    Shows detailed transaction history for the logged-in user.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')

    account = request.user.bank_account
    transactions_list = Transaction.objects.filter(
        Q(sender_account=account) | Q(receiver_account=account)
    ).select_related('sender_account__user', 'receiver_account__user').order_by('-timestamp')

    filter_type = request.GET.get('type')
    if filter_type in ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER']:
        transactions_list = transactions_list.filter(transaction_type=filter_type)

    context = {
        'account': account,
        'transactions': transactions_list,
        'current_filter': filter_type,
    }
    return render(request, 'transactions/statement.html', context)


# ========================================================
# ADMIN ONLY VIEWS
# ========================================================

@user_passes_test(is_admin_or_staff, login_url='login')
def admin_dashboard_view(request):
    """
    Dedicated Admin Banking Portal:
    Displays all customer accounts with creation date, balance, PAN, Aadhar,
    and action links to deposit money exclusively into any selected account.
    """
    query = request.GET.get('q', '').strip()
    accounts = BankAccount.objects.select_related('user').order_by('-created_at')

    if query:
        accounts = accounts.filter(
            Q(account_number__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(pan_number__icontains=query) |
            Q(aadhar_number__icontains=query) |
            Q(phone_number__icontains=query)
        )

    # Key statistics for admin
    total_accounts = BankAccount.objects.count()
    total_deposits_count = Transaction.objects.filter(transaction_type='DEPOSIT').count()
    from django.db.models import Sum
    total_bank_reserve = BankAccount.objects.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

    context = {
        'accounts': accounts,
        'query': query,
        'total_accounts': total_accounts,
        'total_deposits_count': total_deposits_count,
        'total_bank_reserve': total_bank_reserve,
    }
    return render(request, 'admin_portal/admin_dashboard.html', context)


@user_passes_test(is_admin_or_staff, login_url='login')
def admin_deposit_view(request, account_number=None):
    """
    Exclusively allows Admin to deposit money into a specific account.
    If admin adds money to Account 1, funds are added strictly and only to Account 1.
    """
    initial_data = {}
    target_account = None

    if account_number:
        target_account = get_object_or_404(BankAccount, account_number=account_number)
        initial_data['target_account_number'] = target_account.account_number

    if request.method == 'POST':
        form = AdminDepositForm(request.POST)
        if form.is_valid():
            acc_num = form.cleaned_data['target_account_number']
            amount = form.cleaned_data['amount']
            note = form.cleaned_data.get('deposit_note', '') or 'Branch Deposit by Admin'

            try:
                with transaction.atomic():
                    # Lock only the designated target account
                    account_to_credit = BankAccount.objects.select_for_update().get(account_number=acc_num)
                    
                    # Strictly credit ONLY this account
                    account_to_credit.balance += amount
                    account_to_credit.save()

                    # Create Deposit Transaction
                    txn = Transaction.objects.create(
                        transaction_type='DEPOSIT',
                        sender_account=None,
                        receiver_account=account_to_credit,
                        amount=amount,
                        status='SUCCESS',
                        description=f"{note} (Admin: {request.user.username})",
                        initiated_by=request.user
                    )

                messages.success(
                    request,
                    f"Deposit Successful! Credited ₹{amount:,.2f} exclusively to A/C {account_to_credit.account_number} ({account_to_credit.user.get_full_name() or account_to_credit.user.username}). New Balance: ₹{account_to_credit.balance:,.2f}"
                )
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f"Deposit could not be processed: {str(e)}")
    else:
        form = AdminDepositForm(initial=initial_data)

    context = {
        'form': form,
        'target_account': target_account,
    }
    return render(request, 'admin_portal/admin_deposit.html', context)


@user_passes_test(is_admin_or_staff, login_url='login')
def admin_account_detail_view(request, account_number):
    """
    Allows Admin to inspect full KYC credentials and comprehensive ledger of an account.
    """
    account = get_object_or_404(BankAccount.objects.select_related('user'), account_number=account_number)
    transactions = Transaction.objects.filter(
        Q(sender_account=account) | Q(receiver_account=account)
    ).order_by('-timestamp')

    context = {
        'account': account,
        'transactions': transactions,
    }
    return render(request, 'admin_portal/account_detail.html', context)


@login_required
def verify_account_api(request):
    """
    AJAX endpoint for validating account existence and recipient name dynamically.
    """
    acc_num = request.GET.get('account_number', '').strip()
    if not acc_num:
        return JsonResponse({'valid': False, 'message': 'Account number required.'})

    try:
        acc = BankAccount.objects.select_related('user').get(account_number=acc_num, is_active=True)
        return JsonResponse({
            'valid': True,
            'holder_name': acc.user.get_full_name() or acc.user.username,
            'is_self': request.user.is_authenticated and hasattr(request.user, 'bank_account') and request.user.bank_account.account_number == acc_num
        })
    except BankAccount.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Account not found or inactive.'})
