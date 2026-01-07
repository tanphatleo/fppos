from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)  # Ensure `id` is the primary key
    code = models.CharField(max_length=10, unique=True, blank=True)  # Code remains a unique field
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='invoices')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='invoices')
    date = models.DateField()  # Change to allow user input
    time = models.TimeField()  # Change to allow user input
    final_total = models.DecimalField(max_digits=10, decimal_places=0, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.TextField()  # Change to a text field to save address as plain text
    note = models.TextField(blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    surcharges = JSONField(blank=True, null=True)  # JSON field for surcharge details
    payment_method = models.TextField()
    CHOSEN_DISCOUNT_METHOD_CHOICES = [
        ('percentage', 'Percentage'),
        ('value', 'Value'),
    ]
    chosen_discount_method = models.CharField(max_length=10, choices=CHOSEN_DISCOUNT_METHOD_CHOICES)
    discount_method_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transport_company = models.TextField()
    amount_paid_transport_company = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.code

@receiver(pre_save, sender=Invoice)
def generate_invoice_code(sender, instance, **kwargs):
    if not instance.code:
        last_invoice = sender.objects.order_by('-id').first()
        next_number = int(last_invoice.code[2:]) + 1 if last_invoice and last_invoice.code else 1
        instance.code = f"HD{next_number:08d}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='invoice_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    package_details = JSONField(blank=True, null=True)  # JSON field for normal products in a package

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"
