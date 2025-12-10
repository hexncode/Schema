"""
Generator URL Configuration
"""
from django.urls import path
from generator import views

app_name = 'generator'

urlpatterns = [
    # Building generator page
    path('building-generator/', views.building_generator, name='building_generator'),
]
