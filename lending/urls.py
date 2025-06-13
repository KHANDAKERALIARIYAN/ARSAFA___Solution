from django.urls import path
from . import views

urlpatterns = [
    path('', views.lending_dashboard, name='lending_dashboard'),
    path('create/', views.lending_create, name='lending_create'),
    path('update/<int:pk>/', views.lending_update, name='lending_update'),
    path('delete/<int:pk>/', views.lending_delete, name='lending_delete'),
] 