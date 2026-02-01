from rest_framework import serializers
from .models import Account, TransactionType, Transaction, AccountBalance, DateEndCashBalance

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
    bank_account_name = serializers.SerializerMethodField()
    invoice_code = serializers.CharField(source='invoice.code', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__' 
        extra_fields = [ 'transaction_type_name', 'bank_account_name', 'invoice_code']

    def get_transaction_type_name(self, obj):
        return obj.transaction_type.name

    def get_bank_account_name(self, obj):
        return f"{obj.account.bank_name} - {obj.account.account_number}"

class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountBalance
        fields = '__all__'

class DateEndCashBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateEndCashBalance
        fields = '__all__'
