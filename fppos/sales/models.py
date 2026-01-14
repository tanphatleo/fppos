import random
import string
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)  # Ensure `id` is the primary key
    code = models.CharField(max_length=50, unique=True, blank=True)  # Code remains a unique field
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='invoices')
    date = models.DateField()  # Change to allow user input
    time = models.TimeField()  # Change to allow user input
    final_total = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.TextField(blank=True, null=True)  # Change to a text field to save address as plain text
    note = models.TextField(blank=True, null=True)
    discount = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    total_surcharge = models.IntegerField(default=0)
    surcharges = models.JSONField(blank=True, null=True)  # JSON field for surcharge details
    payment_method = models.TextField(blank=True, null=True)
    payment_account = models.ForeignKey('transactions.Account', on_delete=models.SET_NULL, null=True, blank=True)
    discount_method_value = models.IntegerField(default=0)
    transport_company = models.TextField(blank=True, null=True)
    amount_paid_transport_company = models.IntegerField(default=0)
    amount_paid_by_customer = models.IntegerField(default=0)
    ecom_fee = models.IntegerField(default=0)
    ecom_feestructure = models.JSONField(blank=True, null=True)  # JSON field for e-commerce fee structure
    items = models.JSONField(blank=True, null=True)  # JSON field to store invoice items
    channel = models.CharField(max_length=50, blank=True, null=True)
    seller = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='sold_by_invoices')
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    updated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='updated_invoices')
    def __str__(self):
        return self.code

    @property
    def expanded_items(self):
        result = []
        if self.items and isinstance(self.items, list):
            for item in self.items:
                product_type = item.get('product_type', 'normal')
                code = item.get('code')
                try:
                    quantity = float(item.get('quantity', 0))
                except (ValueError, TypeError):
                    quantity = 0

                result.append({'code': code, 'quantity': quantity, 'type': product_type, 'original_item': None, 'price': item.get('price', 0) , 'original_name': item.get('name', '')})

                if product_type == 'combo':
                    package_details = item.get('package_details')
                    if isinstance(package_details, list):
                        for detail in package_details:
                            detail_code = detail.get('code')
                            try:
                                detail_qty = float(detail.get('quantity', 0))
                            except (ValueError, TypeError):
                                detail_qty = 0
                            result.append({'code': detail_code, 'quantity': quantity * detail_qty, 'type': 'combo_item', 'original_item': code, 'price': None, 'original_name': None})
        return result

# Signal: When Invoice is set to inactive, set all related Transactions to inactive
@receiver(post_save, sender=Invoice)
def set_transactions_inactive_when_invoice_inactive(sender, instance, **kwargs):
    if instance.is_active is False:
        from transactions.models import Transaction
        Transaction.objects.filter(invoice=instance, is_active=True).update(is_active=False)

@receiver(pre_save, sender=Invoice)
def generate_invoice_code(sender, instance, **kwargs):
    if not instance.code:
        date_part = instance.date.strftime('%y%m%d') if instance.date else timezone.now().strftime('%y%m%d')
        random_alpha = ''.join(random.choices(string.ascii_uppercase, k=2))
        random_num = ''.join(random.choices(string.digits, k=3))
        instance.code = f"HD{date_part}{random_alpha}{random_num}"

class Surcharge(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    description = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
