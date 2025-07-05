from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_report, name='sales_report'),
] 