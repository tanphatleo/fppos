from django.db import models

# Create your models here.

class LogicConfig(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.key