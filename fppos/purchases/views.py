from rest_framework import viewsets
from .models import Purchase
from .serializers import PurchaseSerializer
import pandas as pd
from django.http import HttpResponse
from io import BytesIO

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export')
        if export == 'true':
            queryset = self.filter_queryset(self.get_queryset())
            # create excel file
            data = []
            for purchase in queryset:
                base_row = {
                    'Code': purchase.code,
                    'Supplier': purchase.supplier,
                    'Date': purchase.date,
                    'Is Active': purchase.is_active,
                    'Created At': purchase.created_at.replace(tzinfo=None) if purchase.created_at else None,
                    'Updated At': purchase.updated_at.replace(tzinfo=None) if purchase.updated_at else None,
                }
                
                items = purchase.items
                if items and isinstance(items, list) and len(items) > 0:
                    for item in items:
                        row = base_row.copy()
                        row.update({
                            'Item Code': item.get('code', ''),
                            'Item Name': item.get('name', ''),
                            'Item Quantity': item.get('quantity', 0)
                        })
                        data.append(row)
                else:
                    data.append(base_row)

            df = pd.DataFrame(data)
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Purchases')
            writer.close()
            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="purchases.xlsx"'
            return response

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Purchase.objects.all().order_by('-date')
        date_from = self.request.query_params.get('dateFrom')
        date_to = self.request.query_params.get('dateTo')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset
