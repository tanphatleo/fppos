from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.parsers import MultiPartParser
import json
import pandas as pd
import os
from django.conf import settings
from django.http import HttpResponse, FileResponse
from io import BytesIO

from .models import Invoice, Surcharge
from .serializers import InvoiceSerializer, SurchargeSerializer
from transactions.models import Transaction, TransactionType, Account
from logicconfig.models import LogicConfig
from customers.models import Customer
from products.models import Product

# import users
from django.contrib.auth.models import User

# Create your views here.



class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()

    serializer_class = InvoiceSerializer

    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export')
        if export == 'true':
            queryset = self.filter_queryset(self.get_queryset())
            # create excel file
            data = []
            for invoice in queryset:
                root_row = {
                    'Code': invoice.code,
                    'Customer': invoice.customer.name if invoice.customer else '',
                    'Date': invoice.date,
                    'Time': invoice.time,
                    'Total': invoice.total,
                    'Discount': invoice.discount,
                    'Total before surcharge': invoice.total - invoice.total_surcharge,
                    'Surcharge Total': invoice.total_surcharge,
                    'Final Total': invoice.final_total,
                    'Payment Method': invoice.payment_method,
                    'Payment Account': invoice.payment_account.bank_name + ' - ' + invoice.payment_account.account_number if invoice.payment_account else '',
                    'Channel': invoice.channel,
                    'Is Active': invoice.is_active,
                    'Seller': invoice.seller.username if invoice.seller else '',
                }
                base_row = {
                    'Code': invoice.code,
                    'Customer': invoice.customer.name if invoice.customer else '',
                    'Date': invoice.date,
                    'Time': '',
                    'Total': 0,
                    'Discount': 0,
                    'Total before surcharge': 0,
                    'Surcharge Total': 0,
                    'Final Total': 0,
                    'Payment Method': invoice.payment_method,
                    'Payment Account': invoice.payment_account.bank_name + ' - ' + invoice.payment_account.account_number if invoice.payment_account else '',
                    'Channel': invoice.channel,
                    'Is Active': invoice.is_active,
                    'Seller': invoice.seller.username if invoice.seller else '',
                }
                # data.append(base_row)
                expanded_items = invoice.expanded_items
                if expanded_items:
                    i = 0
                    for item in expanded_items:
                        row = base_row.copy()
                        if i == 0:
                            row = root_row.copy()
                        row.update({
                            'Item Code': item.get('code'),
                            'Item Quantity': item.get('quantity'),
                            'Item Type': item.get('type'),
                            'Item Original': item.get('original_item'),
                            'Item Price': item.get('price'),
                            'Item Original Name': item.get('original_name'),
                        })
                        data.append(row)
                        i += 1

                surcharges = invoice.surcharges
                if surcharges and isinstance(surcharges, list):
                    for surcharge in surcharges:
                        row = base_row.copy()
                        row.update({
                            'Item Code': surcharge.get('code'),
                            'Item Quantity': 1,
                            'Item Type': 'surcharge',
                            'Item Original': None,
                            'Item Price': surcharge.get('amount'),
                            'Item Original Name': surcharge.get('description'),
                        })
                        data.append(row)
           
            df = pd.DataFrame(data)

            # all products to ref product prices
            products = Product.objects.all()
            product_price_map = {product.code: product.price for product in products}
            product_name_map = {product.code: product.name for product in products}
            # only map to items that Item Type in ['normal', 'combocombo_item']
            df['Item Unit Price'] = df.apply(lambda row: product_price_map.get(row['Item Code'], 0) 
                                        if row.get('Item Type') in ['normal', 'combo_item'] else 0, axis=1)
            df['Item Unit Price x Quantity'] = df['Item Unit Price'] * df['Item Quantity']
            df['Percentage'] = df['Item Unit Price x Quantity'] / df.groupby('Code')['Item Unit Price x Quantity'].transform('sum')
            df['Percentage'] = df['Percentage'].fillna(0)
            df['Real Price'] = df.groupby('Code')['Total before surcharge'].transform('sum') * df['Percentage']
            df['Item Original Name'] = df.apply(lambda row: product_name_map.get(row['Item Code'], '') 
                                        if row.get('Item Type') in ['combo_item'] else row['Item Original Name'], axis=1)
            
            # for Item Type surcharge, set Real Price to be Item Price
            df['Real Price'] = df.apply(lambda row: row['Item Price'] if row['Item Type'] == 'surcharge' else row['Real Price'], axis=1)
            

            # Remove timezone info from datetime columns for Excel compatibility
            for col in ['Created At', 'Updated At']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: x.replace(tzinfo=None) if x else None)

            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Invoices')
            writer.close()
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
            return response

        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        Invoice.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # add seller as created_by to serializer save
        serializer.is_valid(raise_exception=True)
        invoice_instance = serializer.save(seller_id=request.user.id, created_by_id=request.user.id)

        # Create customer payment transaction
        payment_method = request.data.get('payment_method')
        amount_paid_by_customer = request.data.get('amount_paid_by_customer', 0)
    
        # if amount_paid_by_customer > final_total, set to final_total
        if amount_paid_by_customer > invoice_instance.final_total:
            amount_paid_by_customer = invoice_instance.final_total


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
        print('amount_paid_transport_company:', request.data.get('amount_paid_transport_company'))
        amount_paid_transport_company = request.data.get('amount_paid_transport_company')
        if (amount_paid_transport_company is not None and int(amount_paid_transport_company) > 0):
            Transaction.objects.create(
                transaction_type=TransactionType.objects.get(id=3),  # Assuming 3 is 'Chi tiền cho công ty vận chuyển'
                debit_or_credit='CR',
                amount=amount_paid_transport_company,
                invoice=invoice_instance,
                account=Account.objects.get(id=1), # Assuming 1 is the ID for Cash Account
                description='Thanh toán cho công ty vận chuyển cho hóa đơn ' + invoice_instance.code
            )
        
        headers = self.get_success_headers(serializer.data)
        # Re-fetch and serialize the instance to include the newly created transactions
        return Response(self.get_serializer(invoice_instance).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # set updated_by to request.user
        request.data['updated_by'] = request.user.id

        print('Received payload:', request.data)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Invoice.objects.all().order_by('-date')
        date_from = self.request.query_params.get('dateFrom')
        date_to = self.request.query_params.get('dateTo')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset
    
class SurchargeViewSet(viewsets.ModelViewSet):
    queryset = Surcharge.objects.all()
    serializer_class = SurchargeSerializer

@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_shopee(request):
    
    if 'file' not in request.FILES:
        return Response({"message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        config = LogicConfig.objects.get(key="shopee_map")
        print("Shopee mapping config:", config)
        mapping = json.loads(config.value)
        print("Mapping loaded:", mapping)

        target_columns = [item['name'] for item in mapping]
        print("Target columns:", target_columns)


        df = pd.read_excel(request.FILES['file'])
        
        valid_columns = [col for col in target_columns if col in df.columns]
        df = df[valid_columns]

        # rename columns based on mapping
        rename_dict = {item['name']: item['id'] for item in mapping if item['name'] in df.columns}
        df.rename(columns=rename_dict, inplace=True)
        # df.to_clipboard(index=False)


        required_columns = ['code', 'temp_status', 'transport_company', 
         'product_code', 'quant', 'discount_code_value', 
         'discount_combo_value', 'discount_trade_in_value', 'date', 
         'standard_fee', 'service_fee', 'payment_fee', 'price',
         'customer', 'customer_name', 'customer_phone', 'delivery_address','product_name','product_name_after']
        # check if all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        # for each item in missing map to 'name' in mapping
        convert_to_shoppee_columns = [item['name'] for item in mapping if item['id'] in missing_columns]
        if missing_columns:
            return Response({"message": f"Missing columns: {', '.join(convert_to_shoppee_columns)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # all products to check if products in file exist
        products = Product.objects.all()
        product_code_map = {product.code: product for product in products}
        # check if all product codes in df exist in products
        missing_products = set()
        for code in df['product_code'].unique():
            if code not in product_code_map:
                missing_products.add(code)
        if missing_products:
            return Response({"message": f"Missing products in system: {', '.join(missing_products)}"}, status=status.HTTP_400_BAD_REQUEST)

        # create customer dataframe from customer	customer_name	customer_phone	delivery_address
        customer_df = df[['customer', 'customer_name', 'customer_phone', 'delivery_address']].drop_duplicates()
        # update or create customers
        for index, row in customer_df.iterrows():
            # print(row)
            customer, created = Customer.objects.update_or_create(
                code='SP_' + str(row['customer']),
                defaults={
                    'name': row['customer_name'],
                    'phone_number': row['customer_phone'],
                    'address': row['delivery_address']
                }
            )
        print("Customer processing done.")
        # Filter out rows where date is not set
        df = df.dropna(subset=['date'])

        # Helper to parse floats safely
        def get_val(val):
            v = pd.to_numeric(val, errors='coerce')
            return 0 if pd.isna(v) else v

        # Pre-fetch combo products to avoid N+1 queries
        combo_products = Product.objects.filter(product_type='combo')
        combo_map = {p.code: p.package_details for p in combo_products}

        # Group by invoice code
        grouped = df.groupby('code')

        for code, group in grouped:
            first_row = group.iloc[0]
            
            # Date and Time
            date_val = pd.to_datetime(first_row['date'], errors='coerce')
            if pd.isna(date_val):
                continue

            # Determine is_active
            is_active = True
            if first_row.get('temp_status') == 'Đã hủy':
                is_active = False

            # Get Customer
            customer_code = 'SP_' + str(first_row['customer'])
            customer_obj = Customer.objects.filter(code=customer_code).first()
            
            if not customer_obj:
                continue

            # Items
            items = []
            total_amount = 0
            for _, row in group.iterrows():
                quantity = get_val(row.get('quant'))
                price = get_val(row.get('price'))
                
                line_total = quantity * price
                
                product_code = row.get('product_code', '')
                
                product_type = "normal"
                package_details = None
                
                if product_code in combo_map:
                    product_type = "combo"
                    package_details = combo_map[product_code]

                items.append({
                    "code": product_code,
                    "name": str(row.get('product_name', '')) + ' - ' + str(row.get('product_name_after', '')),
                    "note": "", 
                    "hasNote": False,
                    "quantity": quantity,
                    "price": price,
                    "total": line_total,
                    "product_type": product_type,
                    "package_details": package_details,
                    "isOpenPopover": False
                })
                total_amount += line_total

            # Discounts & Fees
            discount = get_val(first_row.get('discount_code_value')) + \
                       get_val(first_row.get('discount_combo_value')) + \
                       get_val(first_row.get('discount_trade_in_value'))
            
            service_fee = get_val(first_row.get('service_fee'))
            payment_fee = get_val(first_row.get('payment_fee'))
            ecom_fee = service_fee + payment_fee
            ecom_feestructure = {
                "service_fee": service_fee,
                "payment_fee": payment_fee
            }

            final_total = total_amount - discount
            
            invoice_defaults = {
                'customer': customer_obj,
                'date': date_val.date(),
                'time': date_val.time(),
                'is_active': is_active,
                'items': items,
                'total': total_amount,
                'discount': discount,
                'final_total': final_total,
                'channel': 'Shopee',
                'payment_method': 'Shopee',
                'delivery_address': first_row.get('delivery_address', ''),
                'transport_company': first_row.get('transport_company', ''),
                'amount_paid_transport_company': get_val(first_row.get('standard_fee')),
                'amount_paid_by_customer': 0,
                'ecom_fee': ecom_fee,
                'ecom_feestructure': ecom_feestructure,
                'updated_by': request.user if request.user.is_authenticated else None,
                #  seller is id = 4
                'seller': User.objects.get(id=4),
            }
            
            invoice, created = Invoice.objects.update_or_create(
                code="SP_" + str(code),
                defaults=invoice_defaults
            )
            
            if created and request.user.is_authenticated:
                invoice.created_by = request.user
                invoice.save()

        print("Processed DataFrame columns:", df.head())
        print("Processed DataFrame columns:", df.columns.tolist())

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "OK"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def download_purchase_template(request):
    file_path = os.path.join(settings.BASE_DIR, 'sales', 'MauFileNhapHang.xlsx')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='MauFileNhapHang.xlsx')
    return Response({"message": "File not found"}, status=status.HTTP_404_NOT_FOUND)
