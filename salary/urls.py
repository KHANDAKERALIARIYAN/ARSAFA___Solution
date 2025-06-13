from django.urls import path
from . import views

urlpatterns = [
    path('', views.salary_calculation, name='salary_calculation'),
] 