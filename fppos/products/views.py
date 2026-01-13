from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, ProductGroup, DateEndInventory
from .serializers import ProductSerializer, ProductGroupSerializer, DateEndInventorySerializer
from sales.models import Invoice
from purchases.models import Purchase
from sales.serializers import InvoiceSerializer
from purchases.serializers import PurchaseSerializer
# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductGroupViewSet(viewsets.ModelViewSet):
    queryset = ProductGroup.objects.all()
    serializer_class = ProductGroupSerializer

class DateEndInventoryViewSet(viewsets.ModelViewSet):
    queryset = DateEndInventory.objects.all().order_by('-date')
    serializer_class = DateEndInventorySerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        dayend = self.request.query_params.get('dayend')
        date = self.request.query_params.get('date')

        if dayend == 'true' and date:
            invoices = Invoice.objects.filter(date=date, is_active=True)
            purchases = Purchase.objects.filter(date=date, is_active=True)

            target = None
            if isinstance(response.data, list) and len(response.data) > 0:
                target = response.data[0]
            
            if target:
                target['invoices'] = InvoiceSerializer(invoices, many=True).data
                target['purchases'] = PurchaseSerializer(purchases, many=True).data
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        dayend = self.request.query_params.get('dayend')
        date = self.request.query_params.get('date')
        if dayend == 'true' and date:
            queryset = queryset.filter(date=date, is_active=True)
        return queryset

    def perform_create(self, serializer):
        date = serializer.validated_data.get('date')
        if date:
            DateEndInventory.objects.filter(date=date).update(is_active=False)
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
