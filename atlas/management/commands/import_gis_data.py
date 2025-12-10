"""
Import GIS data from GeoPackage files into PostGIS database.

Usage:
    python manage.py import_gis_data                    # Import all layers
    python manage.py import_gis_data --layer Lots      # Import specific layer
    python manage.py import_gis_data --clear           # Clear existing data first
    python manage.py import_gis_data --batch-size 5000 # Custom batch size
"""
import os
import sys
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Import GIS data from GeoPackage files into PostGIS database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--layer',
            type=str,
            help='Specific layer to import (e.g., Lots, Suburb)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Number of features to insert per batch (default: 5000)',
        )
        parser.add_argument(
            '--source-dir',
            type=str,
            default=None,
            help='Source directory for GeoPackage files',
        )

    def handle(self, *args, **options):
        # Check if PostGIS is enabled
        if not getattr(settings, 'USE_POSTGIS', False):
            raise CommandError(
                'PostGIS is not enabled. Set USE_POSTGIS=True in environment variables.\n'
                'Example: USE_POSTGIS=True python manage.py import_gis_data'
            )

        # Import GIS libraries
        try:
            import geopandas as gpd
            from shapely import wkt
            from shapely.geometry import mapping, MultiPolygon, Polygon
        except ImportError as e:
            raise CommandError(f'Required GIS library not installed: {e}')

        # Get source directory
        source_dir = options['source_dir']
        if source_dir:
            layers_path = Path(source_dir)
        else:
            layers_path = settings.BASE_DIR / 'atlas' / 'gis' / 'Layers' / 'NSW'

        if not layers_path.exists():
            raise CommandError(f'Layers directory not found: {layers_path}')

        self.stdout.write(f'Source directory: {layers_path}')

        # Define layer mappings
        layer_configs = {
            'Lots': {
                'file': 'Lots.gpkg',
                'model': 'CadastralLot',
                'field_mapping': {
                    'lot_id': ['cadid', 'lotidstring', 'objectid'],
                    'lot_number': ['lotnumber', 'lot'],
                    'plan_number': ['plannumber', 'plan', 'planid'],
                    'plan_label': ['planlabel'],
                    'address': ['address', 'propaddress'],
                    'area_sqm': ['area', 'shape_area', 'areasqm'],
                    'lga': ['lganame', 'lga', 'lgacode'],
                    'parish': ['parish', 'parishname'],
                }
            },
            'Suburb': {
                'file': 'Suburb.gpkg',
                'model': 'Suburb',
                'field_mapping': {
                    'suburb_name': ['suburbname', 'name', 'loc_name', 'suburb'],
                    'postcode': ['postcode', 'pcode'],
                    'lga': ['lganame', 'lga'],
                    'area_sqkm': ['area', 'shape_area'],
                }
            }
        }

        # Determine which layers to import
        if options['layer']:
            layer_name = options['layer']
            if layer_name not in layer_configs:
                available = ', '.join(layer_configs.keys())
                raise CommandError(f'Unknown layer: {layer_name}. Available: {available}')
            layers_to_import = {layer_name: layer_configs[layer_name]}
        else:
            layers_to_import = layer_configs

        batch_size = options['batch_size']
        clear_existing = options['clear']

        # Import each layer
        for layer_name, config in layers_to_import.items():
            gpkg_path = layers_path / config['file']
            if not gpkg_path.exists():
                self.stdout.write(self.style.WARNING(f'File not found: {gpkg_path}, skipping...'))
                continue

            self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
            self.stdout.write(self.style.SUCCESS(f'Importing {layer_name} from {config["file"]}'))
            self.stdout.write(self.style.SUCCESS(f'{"="*60}'))

            try:
                self._import_layer(
                    gpkg_path=gpkg_path,
                    layer_name=layer_name,
                    config=config,
                    batch_size=batch_size,
                    clear_existing=clear_existing,
                    gpd=gpd,
                    MultiPolygon=MultiPolygon,
                    Polygon=Polygon,
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing {layer_name}: {e}'))
                import traceback
                traceback.print_exc()

        self.stdout.write(self.style.SUCCESS('\nImport complete!'))

    def _import_layer(self, gpkg_path, layer_name, config, batch_size, clear_existing, gpd, MultiPolygon, Polygon):
        """Import a single GIS layer into the database"""
        from atlas.models import GISLayer, CadastralLot, Suburb

        start_time = time.time()

        # Get the model class
        model_map = {
            'CadastralLot': CadastralLot,
            'Suburb': Suburb,
        }
        model_class = model_map.get(config['model'])
        if not model_class:
            raise CommandError(f'Unknown model: {config["model"]}')

        # Clear existing data if requested
        if clear_existing:
            self.stdout.write(f'Clearing existing {layer_name} data...')
            deleted_count = model_class.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} existing records')

        # Read the GeoPackage file
        self.stdout.write(f'Reading {gpkg_path}...')

        # Use pyogrio if available for faster reading
        try:
            import pyogrio
            gdf = gpd.read_file(gpkg_path, engine='pyogrio')
            self.stdout.write('Using pyogrio engine (fast)')
        except ImportError:
            gdf = gpd.read_file(gpkg_path)
            self.stdout.write('Using fiona engine')

        total_features = len(gdf)
        self.stdout.write(f'Loaded {total_features:,} features')

        # Convert CRS to WGS84 (EPSG:4326) if needed
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            self.stdout.write(f'Converting from {gdf.crs} to EPSG:4326...')
            gdf = gdf.to_crs(epsg=4326)

        # Get column name mapping (case-insensitive)
        gdf.columns = [c.lower() for c in gdf.columns]
        available_columns = set(gdf.columns)

        def find_column(possible_names):
            """Find first matching column from list of possibilities"""
            for name in possible_names:
                if name.lower() in available_columns:
                    return name.lower()
            return None

        # Build field mapping
        field_mapping = {}
        for model_field, possible_columns in config['field_mapping'].items():
            col = find_column(possible_columns)
            if col:
                field_mapping[model_field] = col
                self.stdout.write(f'  {model_field} <- {col}')

        # Import in batches
        self.stdout.write(f'\nImporting {total_features:,} features in batches of {batch_size:,}...')

        imported_count = 0
        error_count = 0
        batch_objects = []

        for idx, row in gdf.iterrows():
            try:
                # Get geometry
                geom = row.geometry
                if geom is None or geom.is_empty:
                    error_count += 1
                    continue

                # Ensure MultiPolygon
                if isinstance(geom, Polygon):
                    geom = MultiPolygon([geom])
                elif not isinstance(geom, MultiPolygon):
                    # Try to convert
                    if hasattr(geom, 'geoms'):
                        polys = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
                        if polys:
                            geom = MultiPolygon(polys) if len(polys) > 1 else MultiPolygon([polys[0]])
                        else:
                            error_count += 1
                            continue
                    else:
                        error_count += 1
                        continue

                # Fix invalid geometry
                if not geom.is_valid:
                    geom = geom.buffer(0)
                    if not geom.is_valid:
                        error_count += 1
                        continue

                # Build model instance
                obj_kwargs = {'geom': geom.wkt}

                for model_field, source_col in field_mapping.items():
                    value = row.get(source_col)
                    if value is not None and str(value) not in ['nan', 'None', '']:
                        # Handle numeric fields
                        if model_field in ['area_sqm', 'area_sqkm']:
                            try:
                                obj_kwargs[model_field] = float(value)
                            except (ValueError, TypeError):
                                pass
                        else:
                            obj_kwargs[model_field] = str(value)[:300]  # Truncate long strings

                batch_objects.append(model_class(**obj_kwargs))
                imported_count += 1

                # Insert batch
                if len(batch_objects) >= batch_size:
                    self._insert_batch(model_class, batch_objects)
                    batch_objects = []
                    progress = (imported_count / total_features) * 100
                    elapsed = time.time() - start_time
                    rate = imported_count / elapsed if elapsed > 0 else 0
                    self.stdout.write(
                        f'  Progress: {imported_count:,}/{total_features:,} ({progress:.1f}%) '
                        f'- {rate:.0f} features/sec'
                    )

            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    self.stdout.write(self.style.WARNING(f'  Error at row {idx}: {e}'))

        # Insert remaining batch
        if batch_objects:
            self._insert_batch(model_class, batch_objects)

        elapsed = time.time() - start_time

        # Update GISLayer metadata
        layer_meta, created = GISLayer.objects.update_or_create(
            name=layer_name,
            defaults={
                'display_name': layer_name.replace('_', ' ').title(),
                'category': 'NSW',
                'source_file': str(gpkg_path),
                'feature_count': imported_count,
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS(
            f'\n{layer_name} import complete:'
            f'\n  - Imported: {imported_count:,} features'
            f'\n  - Errors: {error_count:,}'
            f'\n  - Time: {elapsed:.1f} seconds'
            f'\n  - Rate: {imported_count/elapsed:.0f} features/second'
        ))

    def _insert_batch(self, model_class, objects):
        """Insert a batch of objects using bulk_create"""
        with transaction.atomic():
            model_class.objects.bulk_create(objects, ignore_conflicts=True)
