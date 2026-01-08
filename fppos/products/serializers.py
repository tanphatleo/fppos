from rest_framework import serializers
from .models import Product, ProductGroup



class ProductGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroup
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    productGroup = serializers.CharField(source='product_group.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'