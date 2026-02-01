from django.shortcuts import render
from rest_framework import viewsets
from .models import LogicConfig
from .serializers import LogicConfigSerializer

# Create your views here.

class LogicConfigViewSet(viewsets.ModelViewSet):
    queryset = LogicConfig.objects.all()
    serializer_class = LogicConfigSerializer