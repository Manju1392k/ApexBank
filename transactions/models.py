from django.db import models
from django.contrib.auth.models import User
from accounts.models import BankAccount
import uuid

class Transaction(models.Model):
    """
    Records every deposit, withdrawal, and peer-to-peer transfer.
    Supports atomic audit and ledger generation.
    """
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Admin Deposit'),
        ('WITHDRAWAL', 'Cash Withdrawal'),
        ('TRANSFER', 'Account Transfer'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    ]

    reference_id = models.CharField(
        max_length=32, 
        unique=True, 
        editable=False,
        db_index=True
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    sender_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='outgoing_transactions'
    )
    receiver_account = models.ForeignKey(
        BankAccount, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='incoming_transactions'
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='SUCCESS')
    description = models.CharField(max_length=255, blank=True)
    
    # Audit tracking: who initiated the transaction (useful for Admin deposits)
    initiated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='initiated_transactions'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def save(self, *args, **kwargs):
        if not self.reference_id:
            # Generate e.g. TXN-7F8A1B2C3D4E
            self.reference_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_id} - {self.transaction_type} - ₹{self.amount}"
