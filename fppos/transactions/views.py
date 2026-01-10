
from rest_framework import viewsets
from .models import Account, TransactionType, Transaction, AccountBalance
from .serializers import AccountSerializer, TransactionTypeSerializer, TransactionSerializer, AccountBalanceSerializer

class AccountViewSet(viewsets.ModelViewSet):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
	queryset = TransactionType.objects.all()
	serializer_class = TransactionTypeSerializer

class TransactionViewSet(viewsets.ModelViewSet):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer

class AccountBalanceViewSet(viewsets.ModelViewSet):
	queryset = AccountBalance.objects.all()
	serializer_class = AccountBalanceSerializer
