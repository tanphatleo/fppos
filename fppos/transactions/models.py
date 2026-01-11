from django.db import models

# Create your models here.

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    account_number = models.CharField(max_length=20, unique=True)
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_holder_name} - {self.account_number}"


class TransactionType(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    ]
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    debit_or_credit = models.CharField(max_length=2, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    debit_or_credit = models.CharField(max_length=2, choices=TransactionType.TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    ref = models.CharField(max_length=100, blank=True, null=True)
    ref_model = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class AccountBalance(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    cr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    dr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Balance for {self.account.account_holder_name} - CR: {self.cr_amount}, DR: {self.dr_amount}, Balance: {self.balance}"

