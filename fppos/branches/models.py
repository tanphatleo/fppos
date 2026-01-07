from django.conf import settings
from django.db import models

# Create your models here.

class Branch(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allow_sellers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='branches',
        blank=True
    )

    def __str__(self):
        return f"{self.branch_name}"
