from django.contrib import admin
from .models import BankAccount

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance', 'pan_number', 'aadhar_number', 'is_active', 'created_at')
    search_fields = ('account_number', 'user__username', 'user__first_name', 'user__last_name', 'pan_number', 'aadhar_number')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('account_number', 'created_at', 'updated_at')
