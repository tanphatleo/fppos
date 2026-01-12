from django.db import models
from django.contrib.postgres.fields import JSONField

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('combo', 'Combo'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='normal')
    price = models.IntegerField(default=0)  # Change price to IntegerField
    package_details = models.JSONField(blank=True, null=True)  # JSON field for package contents
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=50, unique=True)  # Add a unique code field for the product
    product_group = models.ForeignKey('ProductGroup', on_delete=models.SET_NULL, null=True, related_name='products')  # Add relation to ProductGroup

    def __str__(self):
        return self.name

class ProductGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DateEndInventory(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    items = models.JSONField(default=list)  # List of items in JSON format
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='date_end_inventories_created')
    updated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='date_end_inventories_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Date End Inventory - {self.date}"

    
