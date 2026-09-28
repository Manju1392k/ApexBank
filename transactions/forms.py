from django import forms
from django.core.exceptions import ValidationError
from accounts.models import BankAccount
from decimal import Decimal

class WithdrawalForm(forms.Form):
    """Customer self-withdrawal form."""
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('100.00'),
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Enter amount (min ₹100)', 'step': '100'}),
        help_text="Minimum withdrawal amount is ₹100.00"
    )
    description = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reason or note (optional)'})
    )


class TransferForm(forms.Form):
    """Peer-to-peer bank transfer form."""
    recipient_account_number = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Recipient 12-digit Account Number', 'id': 'id_recipient'})
    )
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=Decimal('1.00'),
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Amount in ₹', 'step': '1'}),
        help_text="Transfer limit per transaction is ₹5,00,000.00"
    )
    description = forms.CharField(
        max_length=150, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Payment purpose (e.g. Rent, Bill, Personal)'})
    )

    def __init__(self, *args, **kwargs):
        self.sender_account = kwargs.pop('sender_account', None)
        super().__init__(*args, **kwargs)

    def clean_recipient_account_number(self):
        target_number = self.cleaned_data.get('recipient_account_number', '').strip()
        if self.sender_account and self.sender_account.account_number == target_number:
            raise ValidationError("You cannot transfer funds to your own bank account.")
        
        try:
            target_account = BankAccount.objects.select_related('user').get(account_number=target_number, is_active=True)
        except BankAccount.DoesNotExist:
            raise ValidationError("Recipient bank account number not found or is currently inactive.")
        
        return target_number


class AdminDepositForm(forms.Form):
    """Exclusive Admin form for depositing money into customer accounts."""
    target_account_number = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Target Bank Account Number', 'id': 'id_target_account'})
    )
    amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        min_value=Decimal('10.00'),
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Deposit Amount in ₹', 'step': '10'})
    )
    deposit_note = forms.CharField(
        max_length=200, 
        required=False,
        initial="Branch Cash Deposit by Admin",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reference or deposit remarks'})
    )

    def clean_target_account_number(self):
        acc_num = self.cleaned_data.get('target_account_number', '').strip()
        if not BankAccount.objects.filter(account_number=acc_num).exists():
            raise ValidationError(f"No bank account found matching account number '{acc_num}'.")
        return acc_num
