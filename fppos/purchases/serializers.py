from rest_framework import serializers
from .models import Purchase

class PurchaseSerializer(serializers.ModelSerializer):
    total_quantity = serializers.ReadOnlyField()

    class Meta:
        model = Purchase
        fields = '__all__'