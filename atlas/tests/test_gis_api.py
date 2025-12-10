"""
Test GIS API Endpoints
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from app import create_app

def test_api_endpoints():
    """Test the GIS API endpoints"""

    print("=" * 80)
    print("GIS API ENDPOINTS TEST")
    print("=" * 80)

    # Create Flask app
    app = create_app()
    client = app.test_client()

    # Test 1: Get Catalog
    print("\n1. GET /api/gis/catalog")
    print("-" * 80)
    response = client.get('/api/gis/catalog')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            print(f"Total Layers: {data['summary']['total_layers']}")
            print(f"Available Layers: {data['summary']['available_layers']}")
            print(f"Categories: {list(data['catalog']['categories'])}")
            print("Layers:")
            for name, layer in data['catalog']['layers'].items():
                print(f"  - {name}: {layer['display_name']}")
    else:
        print(f"Error: {response.get_json()}")

    # Test 2: Get Layer Info
    print("\n2. GET /api/gis/layer/nsw_lots/info")
    print("-" * 80)
    response = client.get('/api/gis/layer/nsw_lots/info')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            layer = data['layer']
            print(f"Name: {layer['name']}")
            print(f"Display Name: {layer['display_name']}")
            print(f"Description: {layer['description']}")
            print(f"Min Zoom: {layer['min_zoom']}")
            print(f"Exists: {layer['exists']}")

    # Test 3: Get Layer Data (with bbox)
    print("\n3. GET /api/gis/layer/nsw_lots?bbox=151.20,-33.88,151.21,-33.87&zoom=15")
    print("-" * 80)
    response = client.get('/api/gis/layer/nsw_lots?bbox=151.20,-33.88,151.21,-33.87&zoom=15')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        # Response is raw GeoJSON
        import json
        data = json.loads(response.data)
        print(f"Type: {data.get('type')}")
        print(f"Features: {len(data.get('features', []))}")
        if data.get('features'):
            print(f"First feature properties: {list(data['features'][0].get('properties', {}).keys())[:5]}...")

    # Test 4: Search Layers
    print("\n4. GET /api/gis/search?q=lots")
    print("-" * 80)
    response = client.get('/api/gis/search?q=lots')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            print(f"Query: {data['query']}")
            print(f"Results: {data['count']}")
            for result in data['results']:
                print(f"  - {result['name']}: {result['display_name']}")

    # Test 5: Query Point
    print("\n5. POST /api/gis/query/point")
    print("-" * 80)
    response = client.post('/api/gis/query/point',
                          json={'lat': -33.875, 'lon': 151.205, 'layers': ['nsw_lots']})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"Success: {data.get('success')}")
        if data.get('success'):
            results = data.get('results', {})
            print(f"Results: {len(results)} layer(s) with features")
            for layer_name, features in results.items():
                print(f"  - {layer_name}: found features")

    print("\n" + "=" * 80)
    print("API TESTS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_api_endpoints()
