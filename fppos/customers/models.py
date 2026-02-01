from django.db import models
from django.conf import settings
from django.utils.timezone import now
import random

# Create your models here.

def generate_customer_code():
    random_digits = random.randint(10000, 99999)
    return f"KH{now().strftime('%Y%m%d')}{random_digits}"

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50, unique=True, blank=True, null=True, default=generate_customer_code)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    address = models.TextField(blank=True, null=True)
    province = models.ForeignKey('Province', on_delete=models.SET_NULL, null=True, related_name='customers')
    ward = models.ForeignKey('Ward', on_delete=models.SET_NULL, null=True, related_name='customers')
    birthday = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_customers'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='updated_customers'
    )

    def __str__(self):
        return self.code + " - " + self.name

    def save(self, *args, **kwargs):
        print("Saving customer:", self.code)
        # Only generate code if not provided or is None or blank
        if not self.code or str(self.code).strip() == "":
            self.code = generate_customer_code()
        super().save(*args, **kwargs)

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

class Ward(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, related_name='wards')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


