"""
Atlas (GIS) URL Configuration
"""
from django.urls import path
from atlas import views

app_name = 'atlas'

urlpatterns = [
    # Map view
    path('map/', views.map_view, name='map'),

    # Property search endpoints
    path('api/search-property/', views.search_property, name='search_property'),
    path('api/property-details/', views.property_details, name='property_details'),
    path('api/properties-in-bounds/', views.properties_in_bounds, name='properties_in_bounds'),

    # GIS Layer API endpoints
    path('api/gis/catalog/', views.get_gis_catalog, name='gis_catalog'),
    path('api/gis/layer/<str:layer_name>/', views.get_gis_layer, name='gis_layer'),
    path('api/gis/layer/<str:layer_name>/info/', views.get_gis_layer_info, name='gis_layer_info'),
    path('api/gis/query/point/', views.query_gis_point, name='query_gis_point'),
    path('api/gis/search/', views.search_gis_layers, name='search_gis_layers'),

    # Cache management endpoints
    path('api/gis/cache/stats/', views.get_cache_stats, name='cache_stats'),
    path('api/gis/cache/clear/', views.clear_cache, name='clear_cache'),
    # Tile endpoints for chunked loading
    path('api/gis/tiles/<str:layer_name>/', views.get_layer_tiles, name='gis_layer_tiles'),
    path('api/gis/tile/<str:layer_name>/<str:tile_id>/', views.get_layer_tile, name='gis_layer_tile'),

]
