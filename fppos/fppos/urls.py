"""
URL configuration for fppos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, GroupViewSet , user_info
from customers.views import ProvinceViewSet, WardViewSet, CustomerViewSet
from products.views import ChangeItemViewSet, ProductViewSet, ProductGroupViewSet, DateEndInventoryViewSet
from sales.views import InvoiceViewSet, SurchargeViewSet, process_shopee, download_purchase_template
from purchases.views import PurchaseViewSet
from logicconfig.views import LogicConfigViewSet
from customers.views import search_customers
from transactions.views import TransactionViewSet, AccountViewSet, TransactionTypeViewSet, AccountBalanceViewSet, DateEndCashBalanceViewSet



router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'usergroups', GroupViewSet)
router.register(r'provinces', ProvinceViewSet)
router.register(r'wards', WardViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'productgroups', ProductGroupViewSet)
router.register(r'dateendinventories', DateEndInventoryViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'surcharges', SurchargeViewSet)
router.register(r'logicconfigs', LogicConfigViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'transactiontypes', TransactionTypeViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'changeitems', ChangeItemViewSet)
router.register(r'accountbalances', AccountBalanceViewSet)
router.register(r'dateendcashbalances', DateEndCashBalanceViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.jwt')),
    # path('api/v1/', include('djoser.urls.authtoken')),
    path('api/v1/', include(router.urls)),
    path('api/v1/search_customers/', search_customers, name='search_customers'),
    path('api/v1/who_i_am/', user_info, name='user_info'),
    path('api/v1/process_shopee/', process_shopee, name='process_shopee'),
    path('api/v1/download_purchase_template/', download_purchase_template, name='download_purchase_template'),
]
