from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
] 