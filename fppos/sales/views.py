from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Invoice, Surcharge
from .serializers import InvoiceSerializer, SurchargeSerializer

# Create your views here.

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class SurchargeViewSet(viewsets.ModelViewSet):
    queryset = Surcharge.objects.all()
    serializer_class = SurchargeSerializer

class CustomCreateInvoice(APIView):
    def post(self, request, *args, **kwargs):
        print('Received payload:', request.data)
        return Response({'message': 'Payload printed to server console.'}, status=status.HTTP_200_OK)