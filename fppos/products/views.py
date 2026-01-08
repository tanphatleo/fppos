from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, ProductGroup
from .serializers import ProductSerializer, ProductGroupSerializer

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductGroupViewSet(viewsets.ModelViewSet):
    queryset = ProductGroup.objects.all()
    serializer_class = ProductGroupSerializer
