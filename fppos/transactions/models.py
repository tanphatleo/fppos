from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import date
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

class DateEndCashBalance(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(unique=True)
    cash_in_hand = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cash Balance on {self.date} - {self.cash_in_hand}"

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
    date = models.DateField(default=date.today)  # Change to allow user input
    invoice = models.ForeignKey('sales.Invoice', on_delete=models.CASCADE, blank=True, null=True)
    purchase = models.ForeignKey('purchases.Purchase', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


# Signal to update invoice payment fields when a Transaction is saved
@receiver(post_save, sender=Transaction)
def update_invoice_payment_fields(sender, instance, **kwargs):
    if instance.invoice:
        # transaction_type 2: update amount_paid_by_customer
        if instance.transaction_type.id == 2:
            total = sender.objects.filter(invoice=instance.invoice, transaction_type=2, is_active=True).aggregate(models.Sum('amount'))['amount__sum'] or 0
            instance.invoice.amount_paid_by_customer = total
            instance.invoice.save(update_fields=['amount_paid_by_customer'])
        # transaction_type 3: update amount_paid_transport_company
        elif instance.transaction_type.id == 3:
            total = sender.objects.filter(invoice=instance.invoice, transaction_type=3, is_active=True).aggregate(models.Sum('amount'))['amount__sum'] or 0
            instance.invoice.amount_paid_transport_company = total
            instance.invoice.save(update_fields=['amount_paid_transport_company'])


class AccountBalance(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    cr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    dr_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Balance for {self.account.account_holder_name} - CR: {self.cr_amount}, DR: {self.dr_amount}, Balance: {self.balance}"
