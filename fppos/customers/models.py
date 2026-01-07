from django.db import models
from django.conf import settings

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='customers')
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, related_name='customers')  # Add relation to Branch
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
        return self.name

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    country = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Ward(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, related_name='wards')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Address(models.Model):
    street = models.CharField(max_length=255)
    ward = models.ForeignKey('Ward', on_delete=models.SET_NULL, null=True, related_name='addresses')
    province = models.ForeignKey('Province', on_delete=models.SET_NULL, null=True, related_name='addresses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.ward}, {self.province}"

