"""
Cashflow URL Configuration
"""
from django.urls import path
from cashflow import views

app_name = 'cashflow'

urlpatterns = [
    # Cashflow model page
    path('', views.cashflow_index, name='index'),

    # API endpoints
    path('calculate/', views.calculate, name='calculate'),
    path('export/', views.export, name='export'),
]
