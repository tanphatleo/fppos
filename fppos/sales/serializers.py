from rest_framework import serializers
from .models import Invoice, Surcharge


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField(read_only=True)
    customer_phone_number = serializers.SerializerMethodField(read_only=True)
    seller = serializers.CharField(source='seller.username', read_only=True)
    expanded_items = serializers.ReadOnlyField()
    class Meta:
        model = Invoice
        fields = '__all__'
        extra_fields = ['customer_name', 'customer_phone']

    def get_customer_name(self, obj):
        # print("Getting customer name for invoice:", obj.code)
        # Assumes Invoice has a FK to Customer as 'customer' and Customer has 'name'
        return getattr(obj.customer, 'name', None)

    def get_customer_phone_number(self, obj):
        # Assumes Invoice has a FK to Customer as 'customer' and Customer has 'phone_number'
        return getattr(obj.customer, 'phone_number', None)
    
    def get_seller(self, obj):
        return getattr(obj.seller, 'username', None)

class SurchargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Surcharge
        fields = '__all__'