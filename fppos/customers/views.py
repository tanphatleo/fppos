from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer, Province, Ward
from .serializers import CustomerSerializer, ProvinceSerializer, WardSerializer
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated


class ProvinceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer

class WardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ward.objects.all()
    serializer_class = WardSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer

@api_view(['GET'])
def search_customers(request):
    query = request.GET.get('query', '')
    if not query:
        return Response({"error": "Query parameter is required."}, status=400)

    customers = Customer.objects.filter(
        models.Q(name__icontains=query) | models.Q(phone_number__icontains=query) | models.Q(code__icontains=query)
    ).order_by('-created_at')[:20]

    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)
