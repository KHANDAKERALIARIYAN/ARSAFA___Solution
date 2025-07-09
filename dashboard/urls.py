from django.urls import path
from . import views

urlpatterns = [
    path('delete-all-data/', views.delete_all_data, name='delete_all_data'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Placeholder, update as needed
] 