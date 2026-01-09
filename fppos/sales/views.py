from django.shortcuts import render
from rest_framework import viewsets
from .models import Invoice, Surcharge
from .serializers import InvoiceSerializer, SurchargeSerializer

# Create your views here.

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class SurchargeViewSet(viewsets.ModelViewSet):
    queryset = Surcharge.objects.all()
    serializer_class = SurchargeSerializer
