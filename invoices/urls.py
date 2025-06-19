from django.urls import path
from . import views

urlpatterns = [
    # POS URLs
    path('pos/', views.pos_list, name='pos_list'),
    path('pos/create/', views.pos_create, name='pos_create'),
    path('pos/<int:pos_id>/edit/', views.pos_edit, name='pos_edit'),
    path('pos/<int:pos_id>/', views.pos_detail, name='pos_detail'),
    path('pos/<int:pos_id>/delete/', views.pos_delete, name='pos_delete'),
    
    # Invoice URLs
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('api/products/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
] 