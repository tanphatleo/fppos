from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer, Province, Ward
from .serializers import CustomerSerializer, ProvinceSerializer, WardSerializer
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

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
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'code', 'phone_number', 'email']

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-created_at')
        is_active_params = self.request.query_params.getlist('is_active[]')
        if is_active_params:
            # Convert string 'true'/'false' to boolean
            is_active_bools = [val.lower() in ['true', '1'] for val in is_active_params]
            queryset = queryset.filter(is_active__in=is_active_bools)
        return queryset

@api_view(['GET'])
def search_customers(request):
    query = request.GET.get('query', '')
    exclude = request.GET.get('exclude', '')
    if not query:
        return Response({"error": "Query parameter is required."}, status=400)

    queryset = Customer.objects.filter(
        models.Q(name__icontains=query) | models.Q(phone_number__icontains=query) | models.Q(code__icontains=query)
    )

    if exclude:
        print("Excluding customers with code containing:", exclude)
        queryset = queryset.exclude(code__icontains=exclude)

    customers = queryset.order_by('-created_at')[:20]

    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)
