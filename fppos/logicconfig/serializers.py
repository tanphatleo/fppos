from rest_framework import serializers
from .models import LogicConfig

class LogicConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogicConfig
        fields = '__all__'
