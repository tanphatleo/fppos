from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, ProductGroup, DateEndInventory, ChangeItem
from .serializers import ProductSerializer, ProductGroupSerializer, DateEndInventorySerializer, ChangeItemSerializer
from sales.models import Invoice
from purchases.models import Purchase
from sales.serializers import InvoiceSerializer
from rest_framework.response import Response
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
        print("DateEndInventoryViewSet.list called with dayend =", dayend, "and date =", date)
        if dayend == 'true' and date:
            
            invoices = Invoice.objects.filter(date=date, is_active=True)
            purchases = Purchase.objects.filter(date=date, is_active=True)

            target = None
            if isinstance(response.data, list):
                if len(response.data) > 0:
                    target = response.data[0]
                else:
                    # No DateEndInventory found for the given date, create a placeholder
                    change_item_obj = ChangeItem.objects.filter(date=date).first()
                    changes_items_data = change_item_obj.items if change_item_obj else []
                    target = {'date': date, 'is_active': False, 'created_by': None, 'created_at': None, 'updated_by': None, 'items': None , 'previous_date': None, 'changes_items': changes_items_data}
                    response.data.append(target)
            
            if target is not None:
                # Find previous date inventory
                previous_inventory = DateEndInventory.objects.filter(date__lt=date, is_active=True).order_by('-date').first()
                if previous_inventory:
                    target['previous_date'] = DateEndInventorySerializer(previous_inventory).data
                else:
                    target['previous_date'] = None

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

class ChangeItemViewSet(viewsets.ModelViewSet):
    queryset = ChangeItem.objects.all()
    serializer_class = ChangeItemSerializer

    def create(self, request, *args, **kwargs):
        date = request.data.get('date')
        items = request.data.get('items')
        change_item, created = ChangeItem.objects.update_or_create(
            date=date,
            defaults={'items': items}
        )
        serializer = self.get_serializer(change_item)
        return Response(serializer.data)
