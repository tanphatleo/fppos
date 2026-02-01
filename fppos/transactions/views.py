from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets
from .models import Account, TransactionType, Transaction, AccountBalance, DateEndCashBalance
from .serializers import AccountSerializer, TransactionTypeSerializer, TransactionSerializer, AccountBalanceSerializer, DateEndCashBalanceSerializer
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

class AccountViewSet(viewsets.ModelViewSet):
	queryset = Account.objects.all()
	serializer_class = AccountSerializer

class TransactionTypeViewSet(viewsets.ModelViewSet):
	queryset = TransactionType.objects.all()
	serializer_class = TransactionTypeSerializer

class TransactionViewSet(viewsets.ModelViewSet):
	queryset = Transaction.objects.all()
	serializer_class = TransactionSerializer

	def list(self, request, *args, **kwargs):
		export = request.query_params.get('export')
		if export == 'true':
			queryset = self.filter_queryset(self.get_queryset())
			data = []
			for transaction in queryset:
				ref = ''
				if transaction.invoice:
					ref = f"Invoice: {transaction.invoice.code}"
				elif transaction.purchase:
					ref = f"Purchase: {transaction.purchase.code}"

				data.append({
					'ID': transaction.id,
					'Transaction Type': transaction.transaction_type.name,
					'Debit/Credit': transaction.debit_or_credit,
					'Amount': transaction.amount,
					'Account': transaction.account.bank_name + ' - ' + transaction.account.account_number + ' - ' + transaction.account.account_holder_name,
					'Date': transaction.date,
					'Ref': ref,
					'Description': transaction.description,
					'Created At': transaction.created_at.replace(tzinfo=None) if transaction.created_at else None,
					'Updated At': transaction.updated_at.replace(tzinfo=None) if transaction.updated_at else None,
					'Is Active': transaction.is_active,
				})
			df = pd.DataFrame(data)
			output = BytesIO()
			writer = pd.ExcelWriter(output, engine='xlsxwriter')
			df.to_excel(writer, index=False, sheet_name='Transactions')
			writer.close()
			output.seek(0)
			response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
			response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
			return response
		return super().list(request, *args, **kwargs)

	def get_queryset(self):
		queryset = Transaction.objects.all().order_by('-date', '-created_at')
		date_from = self.request.query_params.get('dateFrom')
		date_to = self.request.query_params.get('dateTo')
		if date_from:
			queryset = queryset.filter(date__gte=date_from)
		if date_to:
			queryset = queryset.filter(date__lte=date_to)
		return queryset

	@action(detail=False, methods=['delete'])
	def delete_all(self, request):
		Transaction.objects.all().delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
	
	

class AccountBalanceViewSet(viewsets.ModelViewSet):
	queryset = AccountBalance.objects.all()
	serializer_class = AccountBalanceSerializer

class DateEndCashBalanceViewSet(viewsets.ModelViewSet):
	queryset = DateEndCashBalance.objects.all()
	serializer_class = DateEndCashBalanceSerializer

	def get_queryset(self):
		queryset = super().get_queryset()
		dateend = self.request.query_params.get('dateend')
		date = self.request.query_params.get('date')
		if dateend == 'true' and date:
			queryset = queryset.filter(date=date)
		return queryset

	def list(self, request, *args, **kwargs):
		response = super().list(request, *args, **kwargs)
		dateend = self.request.query_params.get('dateend')
		date = self.request.query_params.get('date')

		if dateend == 'true' and date:
			target = None
			if isinstance(response.data, list):
				if len(response.data) > 0:
					target = response.data[0]
				else:
					target = {'date': date, 'cash_in_hand': 0, 'previous_date': None, 'created_by': None, 'created_at': None, 'updated_by': None	}
					response.data.append(target)
			
			if target:
				previous_balance = DateEndCashBalance.objects.filter(date__lt=date).order_by('-date').first()
				if previous_balance:
					target['previous_date'] = DateEndCashBalanceSerializer(previous_balance).data
				else:
					target['previous_date'] = None

				transactions = Transaction.objects.filter(date=date)
				target['transactions'] = TransactionSerializer(transactions, many=True).data
		return response
