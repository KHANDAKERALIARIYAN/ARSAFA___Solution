from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('update/<int:pk>/', views.customer_update, name='customer_update'),
    path('delete/<int:pk>/', views.customer_delete, name='customer_delete'),
] 