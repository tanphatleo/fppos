from django.db import models

# Create your models here.

class BankAccount(models.Model):
    id = models.AutoField(primary_key=True)
    account_number = models.CharField(max_length=20, unique=True)
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_holder_name} - {self.account_number}"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    ]
    id = models.AutoField(primary_key=True)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


