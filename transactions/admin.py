from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'transaction_type', 'amount', 'status', 'sender_account', 'receiver_account', 'timestamp')
    list_filter = ('transaction_type', 'status', 'timestamp')
    search_fields = ('reference_id', 'sender_account__account_number', 'receiver_account__account_number', 'description')
    readonly_fields = ('reference_id', 'timestamp')
