from rest_framework import serializers
from .models import Account, TransactionType, Transaction, AccountBalance

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        extra_fields = ['transaction_type_name']
    
    def get_transaction_type_name(self, obj):
        return obj.transaction_type.name

class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountBalance
        fields = '__all__'
