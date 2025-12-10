# Schema - Django Property Development Platform

Clean Django application for NSW property development analysis with file-based GIS.

## What It Does

- **Atlas**: GIS mapping with NSW property lots, buildings, suburbs
- **Cashflow**: Development cashflow modeling with waterfall financing
- **Generator**: 3D building form generation

## Structure

```
Schema/
├── atlas/              # GIS app
│   ├── views.py       # API endpoints
│   ├── gis/           # GIS service (geopandas)
│   └── gis_service.py # Service wrapper
├── cashflow/          # Financial modeling
├── generator/         # Building generator
├── frontend/          # Navigation
├── app/
│   ├── templates/     # HTML templates
│   └── static/        # CSS/JS
├── schema_project/    # Django settings
└── manage.py
```

## Installation

### 1. Install GDAL (Required for geopandas)

**Windows - Using Conda (Easiest):**
```bash
conda create -n schema python=3.13
conda activate schema
conda install -c conda-forge geopandas
```

**Windows - Using Wheels:**
1. Download GDAL wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/
2. `pip install GDAL-3.x.x-cpXX-cpXX-win_amd64.whl`
3. `pip install Fiona-1.x.x-cpXX-cpXX-win_amd64.whl`

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Server

```bash
python manage.py runserver
```

Access at: **http://localhost:8000/**

## Key Points

### No Database for GIS
GIS data is file-based using geopandas. Reads from `.gpkg` files on demand. Fast, simple, no PostGIS required.

### Stateless Calculations
Cashflow calculations are stateless - no database persistence. Pure functions.

### Clean Django
- No Flask dependencies
- No GeoDjango complexity
- Standard Django views and routing
- File-based GIS service

## API Endpoints

### Atlas (GIS)
```
GET  /atlas/map/                        - Map interface
GET  /atlas/api/gis/catalog/           - Layer catalog
GET  /atlas/api/gis/layer/<name>/?bbox=... - Get GeoJSON
POST /atlas/api/gis/query/point/       - Query point
POST /atlas/api/search-property/       - Search Lot/DP
```

### Cashflow
```
GET  /cashflow/                         - Interface
POST /cashflow/calculate/               - Calculate model
```

### Generator
```
GET  /generator/building-generator/     - 3D generator
```

## Development

```bash
# Check for issues
python manage.py check

# Create admin user
python manage.py createsuperuser

# Access admin
http://localhost:8000/admin/
```

## Production

```bash
# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn schema_project.wsgi:application --bind 0.0.0.0:8000
```

## GIS Data

GIS data files are in `app/atlas/gis/Layers/NSW/`:
- NSW_Lots.gpkg (5GB)
- BLD_GreaterSydney.gpkg
- Lots.gpkg
- Suburb.gpkg

These are excluded from git due to size. Upload separately to deployment.

## Tech Stack

- Django 5.0
- Geopandas (file-based GIS)
- NumPy Financial (cashflow calculations)
- Plotly (charts)
- Bootstrap 5 (UI)
- Leaflet (maps)

## What Changed from Flask

1. **Routes → Views**: Flask blueprints are now Django views
2. **No GeoDjango**: Using simple file-based geopandas instead
3. **No Database Models**: GIS and cashflow are stateless
4. **Clean Structure**: Standard Django app layout

## License

Copyright © 2024. All rights reserved.
