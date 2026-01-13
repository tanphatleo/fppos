import random
import string
from django.utils import timezone
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    supplier = models.CharField(max_length=255)
    date = models.DateField()
    # total_amount = models.IntegerField(blank=True, null=True)
    items = models.JSONField(default=list)  # List of items in JSON format
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_quantity(self):
        if not isinstance(self.items, list):
            return 0
        return sum(int(item.get('quantity', 0)) for item in self.items if isinstance(item, dict))

    def __str__(self):
        return self.code

@receiver(pre_save, sender=Purchase)
def generate_purchase_code(sender, instance, **kwargs):
    if not instance.code:
        date_part = instance.date.strftime('%Y%m%d') if instance.date else timezone.now().strftime('%Y%m%d')
        random_alpha = ''.join(random.choices(string.ascii_uppercase, k=2))
        random_num = ''.join(random.choices(string.digits, k=3))
        instance.code = f"MH{date_part}{random_alpha}{random_num}"
