
from rest_framework import viewsets
from .models import Account, TransactionType, Transaction, AccountBalance
from .serializers import AccountSerializer, TransactionTypeSerializer, TransactionSerializer, AccountBalanceSerializer
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

	def get_queryset(self):
		queryset = Transaction.objects.all()
		date_from = self.request.query_params.get('dateFrom')
		date_to = self.request.query_params.get('dateTo')
		if date_from:
			queryset = queryset.filter(date__gte=date_from)
		if date_to:
			queryset = queryset.filter(date__lte=date_to)

		export = self.request.query_params.get('export')
		if export == 'true':
			# create excel file
			
			data = []
			for transaction in queryset:
				data.append({
					'ID': transaction.id,
					'Transaction Type': transaction.transaction_type.name,
					'Debit/Credit': transaction.debit_or_credit,
					'Amount': transaction.amount,
					'Account': transaction.account.account_holder_name,
					'Date': transaction.date,
					'Ref': transaction.ref,
					'Ref Model': transaction.ref_model,
					'Description': transaction.description,
					'Created At': transaction.created_at,
					'Updated At': transaction.updated_at,
					'Is Active': transaction.is_active,
				})
			df = pd.DataFrame(data)
			output = BytesIO()
			writer = pd.ExcelWriter(output, engine='xlsxwriter')
			df.to_excel(writer, index=False, sheet_name='Transactions')
			writer.save()
			output.seek(0)
			response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
			response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
			return response
		return queryset

class AccountBalanceViewSet(viewsets.ModelViewSet):
	queryset = AccountBalance.objects.all()
	serializer_class = AccountBalanceSerializer
