from rest_framework import serializers
from .models import Product, ProductGroup, DateEndInventory, ChangeItem



class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    productGroup = serializers.CharField(source='product_group.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class DateEndInventorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    changes_items = serializers.JSONField(read_only=True)

    class Meta:
        model = DateEndInventory
        fields = '__all__'

class ChangeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeItem
        fields = '__all__'