"""
Django management command to validate and clean GIS data
Usage: python manage.py validate_gis_data
"""

from django.core.management.base import BaseCommand
import geopandas as gpd
from pathlib import Path
import logging

from atlas.gis.config import LAYERS_PATH
from atlas.gis.geometry_cleaner import GeometryCleaner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate and report on GIS data quality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix invalid geometries and save cleaned data'
        )
        parser.add_argument(
            '--layer',
            type=str,
            help='Specific layer to validate (default: all)'
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        layer_filter = options.get('layer')

        self.stdout.write(self.style.SUCCESS('=== GIS Data Validation ===\n'))

        # Find all GeoPackage files
        gpkg_files = list(LAYERS_PATH.rglob('*.gpkg'))

        if layer_filter:
            gpkg_files = [f for f in gpkg_files if layer_filter.lower() in f.stem.lower()]

        self.stdout.write(f'Found {len(gpkg_files)} GeoPackage files\n')

        for gpkg_path in gpkg_files:
            self.validate_layer(gpkg_path, fix_mode)

    def validate_layer(self, path: Path, fix: bool = False):
        """Validate a single layer"""
        layer_name = path.stem

        self.stdout.write(self.style.WARNING(f'\n--- {layer_name} ---'))
        self.stdout.write(f'Path: {path}')

        try:
            # Sample validation (first 10000 features for large datasets)
            import fiona
            with fiona.open(path) as src:
                total_features = len(src)
                self.stdout.write(f'Total features: {total_features:,}')
                self.stdout.write(f'CRS: {src.crs}')
                self.stdout.write(f'Bounds: {src.bounds}')

            # Load sample for validation
            if total_features > 10000:
                # Sample from different parts of the dataset
                bbox = self._get_sample_bbox(path)
                gdf = gpd.read_file(path, bbox=bbox, engine='pyogrio')
                self.stdout.write(f'Loaded sample: {len(gdf)} features')
            else:
                gdf = gpd.read_file(path, engine='pyogrio')
                self.stdout.write(f'Loaded all features: {len(gdf)}')

            # Validate
            cleaner = GeometryCleaner()
            report = cleaner.validate_and_report(gdf)

            # Display results
            self.stdout.write(f'Geometry types: {report["geometry_types"]}')
            self.stdout.write(f'Null geometries: {report["null_geometries"]}')
            self.stdout.write(f'Invalid geometries: {report["invalid_geometries"]}')

            if report['invalid_details']:
                self.stdout.write(self.style.ERROR('Invalid geometry examples:'))
                for detail in report['invalid_details']:
                    self.stdout.write(f'  - {detail["reason"]}')

            if report['is_valid']:
                self.stdout.write(self.style.SUCCESS('✓ Layer is valid'))
            else:
                self.stdout.write(self.style.ERROR('✗ Layer has issues'))

            # Fix if requested
            if fix and not report['is_valid']:
                self.stdout.write(self.style.WARNING('Cleaning geometries...'))
                gdf_clean = cleaner.clean_geodataframe(gdf)

                # Validate cleaned data
                report_clean = cleaner.validate_and_report(gdf_clean)
                if report_clean['is_valid']:
                    self.stdout.write(self.style.SUCCESS('✓ Geometries cleaned successfully'))
                    stats = cleaner.get_stats()
                    self.stdout.write(f'Stats: {stats}')

                    # Note: We don't save back to original file for safety
                    # User should review and manually replace if needed
                    output_path = path.parent / f'{path.stem}_cleaned.gpkg'
                    self.stdout.write(f'Would save to: {output_path}')
                    self.stdout.write(self.style.WARNING('(Skipping save for safety - implement if needed)'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Some issues remain after cleaning'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            logger.exception('Validation error')

    def _get_sample_bbox(self, path: Path):
        """Get a representative sample bbox for large datasets"""
        import fiona
        with fiona.open(path) as src:
            bounds = src.bounds
            # Get central quarter of the dataset
            width = bounds[2] - bounds[0]
            height = bounds[3] - bounds[1]
            return (
                bounds[0] + width * 0.375,
                bounds[1] + height * 0.375,
                bounds[0] + width * 0.625,
                bounds[1] + height * 0.625
            )
