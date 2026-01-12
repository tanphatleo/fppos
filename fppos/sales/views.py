from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Invoice, Surcharge
from .serializers import InvoiceSerializer, SurchargeSerializer
from transactions.models import Transaction, TransactionType, Account

# Create your views here.



class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')

    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        # add creating user to the request data
        request.data['created_by'] = request.user.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_instance = serializer.save()

        # Create customer payment transaction
        payment_method = request.data.get('payment_method')
        amount_paid_by_customer = request.data.get('amount_paid_by_customer', 0)

        if payment_method and amount_paid_by_customer and int(amount_paid_by_customer) > 0:
            account_id = None
            description_verb = ''
            if payment_method == 'cash':
                account_id = 1  # Assuming 1 is the ID for Cash Account
                description_verb = 'tiền mặt'
            elif payment_method == 'transfer':
                account_id = request.data.get('payment_account')
                description_verb = 'chuyển khoản'

            if account_id:
                Transaction.objects.create(
                    transaction_type=TransactionType.objects.get(id=2),  # Assuming 2 is 'Thu tiền từ khách hàng'
                    debit_or_credit='DR',
                    amount=amount_paid_by_customer,
                    invoice=invoice_instance,
                    account=Account.objects.get(id=account_id),
                    description=f'Thanh toán {description_verb} cho hóa đơn {invoice_instance.code}'
                )

        # Create transport fee payment transaction
        amount_paid_transport_company = request.data.get('amount_paid_transport_company')
        if (amount_paid_transport_company is not None and int(amount_paid_transport_company) > 0):
            transport_account_id = request.data.get('transport_company_payment_account')
            if transport_account_id:
                Transaction.objects.create(
                    transaction_type=TransactionType.objects.get(id=3),  # Assuming 3 is 'Chi tiền cho công ty vận chuyển'
                    debit_or_credit='CR',
                    amount=amount_paid_transport_company,
                    invoice=invoice_instance,
                    account=Account.objects.get(id=transport_account_id),
                    description='Thanh toán cho công ty vận chuyển cho hóa đơn ' + invoice_instance.code
                )
        
        headers = self.get_success_headers(serializer.data)
        # Re-fetch and serialize the instance to include the newly created transactions
        return Response(self.get_serializer(invoice_instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        print('Received payload:', request.data)
        return super().update(request, *args, **kwargs)
    
class SurchargeViewSet(viewsets.ModelViewSet):
    queryset = Surcharge.objects.all()
    serializer_class = SurchargeSerializer
