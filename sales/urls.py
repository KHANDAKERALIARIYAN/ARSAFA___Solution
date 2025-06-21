from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_report, name='sales_report'),
    # path('list/', views.sales_list, name='sales_list'),
    # path('create/', views.sales_create, name='sales_create'),
    # path('<int:pk>/', views.sales_detail, name='sales_detail'),
] 