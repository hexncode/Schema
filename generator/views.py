"""
Building Generator views - 3D building form generation
"""
from django.shortcuts import render


def building_generator(request):
    """3D Building Form Generator page"""
    return render(request, 'generator/building_generator.html')
