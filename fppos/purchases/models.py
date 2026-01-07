from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True, blank=True)
    supplier = models.CharField(max_length=255)
    date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

@receiver(pre_save, sender=Purchase)
def generate_purchase_code(sender, instance, **kwargs):
    if not instance.code:
        last_purchase = sender.objects.order_by('-id').first()
        next_number = int(last_purchase.code[2:]) + 1 if last_purchase and last_purchase.code else 1
        instance.code = f"MH{next_number:08d}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='purchase_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"
