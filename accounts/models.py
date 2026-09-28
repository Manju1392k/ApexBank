from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import random
import string

def generate_account_number():
    """Generates a unique 12-digit bank account number starting with 6010."""
    prefix = "6010"
    random_digits = "".join(random.choices(string.digits, k=8))
    return f"{prefix}{random_digits}"

class BankAccount(models.Model):
    """
    Primary Bank Account Model holding Customer KYC (PAN, Aadhar), 
    Account Number, and current available balance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_account')
    account_number = models.CharField(
        max_length=16, 
        unique=True, 
        default=generate_account_number, 
        editable=False,
        db_index=True
    )
    
    # Phone number
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?[0-9]{10,15}$', message="Enter a valid contact number (10-15 digits).")]
    )
    
    # PAN Card (Format: ABCDE1234F - 5 uppercase letters, 4 digits, 1 uppercase letter)
    pan_validator = RegexValidator(
        regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
        message="Enter a valid PAN Card number (e.g. ABCDE1234F)."
    )
    pan_number = models.CharField(
        max_length=10, 
        unique=True, 
        validators=[pan_validator],
        help_text="Permanent Account Number (10 alphanumeric characters)"
    )
    
    # Aadhar Card (Format: 12 numeric digits)
    aadhar_validator = RegexValidator(
        regex=r'^[2-9]{1}[0-9]{11}$',
        message="Enter a valid 12-digit Aadhar Card number."
    )
    aadhar_number = models.CharField(
        max_length=12, 
        unique=True, 
        validators=[aadhar_validator],
        help_text="12-digit Indian Aadhar identity number"
    )
    
    # Account status & Balance
    balance = models.DecimalField(
        max_digits=14, 
        decimal_places=2, 
        default=0.00,
        help_text="Current available funds in INR"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Designates whether this bank account is operational."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - A/C: {self.account_number}"

    @property
    def masked_aadhar(self):
        """Returns masked Aadhar like XXXXXXXX1234 for privacy"""
        if self.aadhar_number and len(self.aadhar_number) == 12:
            return f"XXXX-XXXX-{self.aadhar_number[-4:]}"
        return self.aadhar_number

    @property
    def masked_pan(self):
        """Returns masked PAN like XXXXX1234F"""
        if self.pan_number and len(self.pan_number) == 10:
            return f"XXXXX{self.pan_number[5:]}"
        return self.pan_number
