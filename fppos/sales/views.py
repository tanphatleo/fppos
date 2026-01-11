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
    queryset = Invoice.objects.all()

    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        # print('Received payload:', request.data)      


        # create customer payment transaction 
        # check if payment method is provided in the payload
        payment_method = request.data.get('payment_method')

        # create the invoice
        invoice = super().create(request, *args, **kwargs)

        # print(f'Processing payment method: {invoice.data}')
        if payment_method == 'cash':
            # print('Processing cash payment...')
            Transaction.objects.create(
                transaction_type=TransactionType.objects.get(id=2),  # assuming 2 is the ID for Thu tiền từ khách hàng
                debit_or_credit='DR',
                amount=request.data.get('amount_paid_by_customer', 0),
                ref = invoice.data.get('code'),
                ref_model = 'Invoice',
                account=Account.objects.get(id=1),  # assuming 1 is the ID for Cash Account
                description='Thanh toán tiền mặt cho hóa đơn ' + invoice.data.get('code')
            )
            # Add logic for cash payment processing if needed
        elif payment_method == 'transfer':
            # print('Processing transfer payment...')
            Transaction.objects.create(
                transaction_type=TransactionType.objects.get(id=2),  # assuming 2 is the ID for Thu tiền từ khách hàng
                debit_or_credit='DR',
                amount=request.data.get('amount_paid_by_customer', 0),
                ref = invoice.data.get('code'),
                ref_model = 'Invoice',
                account=Account.objects.get(id=request.data.get('payment_account')),  # get account from request data
                description='Thanh toán chuyển khoản cho hóa đơn ' + invoice.data.get('code')
            )
            # Add logic for transfer payment processing if needed

        # check if amount_paid_transport_company is provided in the payload
        amount_paid_transport_company = request.data.get('amount_paid_transport_company')
        if (amount_paid_transport_company is not None and 
            int(amount_paid_transport_company) > 0 ):
            # print(f'Amount paid to transport company: {amount_paid_transport_company}')
            # Add logic for handling transport company payment if needed
            Transaction.objects.create(
                transaction_type=TransactionType.objects.get(id=3),  # assuming 3 is the ID for Chi tiền cho công ty vận chuyển
                debit_or_credit='CR',
                amount=amount_paid_transport_company,
                ref = invoice.data.get('code'),
                ref_model = 'Invoice',
                account=Account.objects.get(id=request.data.get('transport_company_payment_account')),
                description='Thanh toán cho công ty vận chuyển cho hóa đơn ' + invoice.data.get('code')
            )
            

        # create the invoice
        return invoice

    def update(self, request, *args, **kwargs):
        print('Received payload:', request.data)
        return super().update(request, *args, **kwargs)
    
class SurchargeViewSet(viewsets.ModelViewSet):
    queryset = Surcharge.objects.all()
    serializer_class = SurchargeSerializer
