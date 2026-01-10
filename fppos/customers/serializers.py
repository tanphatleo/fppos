from rest_framework import serializers
from .models import Customer, Province, Ward

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    # code = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = '__all__'