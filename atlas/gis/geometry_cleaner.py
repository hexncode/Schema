"""
GIS Geometry Cleaner
Best practices for cleaning and validating GIS data
"""

import geopandas as gpd
import logging
from pathlib import Path
from typing import Optional, Tuple
from shapely import validation
from shapely.geometry import Polygon, MultiPolygon
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class GeometryCleaner:
    """
    Cleans and validates GIS geometries following best practices:
    - Fix invalid geometries
    - Ensure correct CRS
    - Remove duplicate features
    - Simplify where appropriate
    - Validate topology
    """

    def __init__(self):
        self.stats = {
            'total_features': 0,
            'invalid_fixed': 0,
            'null_removed': 0,
            'duplicates_removed': 0,
            'crs_transformed': False
        }

    def clean_geodataframe(
        self,
        gdf: gpd.GeoDataFrame,
        target_crs: str = 'EPSG:4326',
        fix_invalid: bool = True,
        remove_duplicates: bool = True,
        remove_null: bool = True
    ) -> gpd.GeoDataFrame:
        """
        Clean a GeoDataFrame with best practices

        Args:
            gdf: Input GeoDataFrame
            target_crs: Target CRS (default: WGS84)
            fix_invalid: Fix invalid geometries
            remove_duplicates: Remove duplicate geometries
            remove_null: Remove null geometries

        Returns:
            Cleaned GeoDataFrame
        """
        if gdf is None or gdf.empty:
            return gdf

        self.stats['total_features'] = len(gdf)
        original_count = len(gdf)

        # 1. Remove null geometries
        if remove_null:
            null_mask = gdf.geometry.isna() | gdf.geometry.is_empty
            null_count = null_mask.sum()
            if null_count > 0:
                gdf = gdf[~null_mask].copy()
                self.stats['null_removed'] = null_count
                logger.info(f"Removed {null_count} null/empty geometries")

        if gdf.empty:
            return gdf

        # 2. Fix invalid geometries
        if fix_invalid:
            invalid_mask = ~gdf.geometry.is_valid
            invalid_count = invalid_mask.sum()

            if invalid_count > 0:
                logger.info(f"Found {invalid_count} invalid geometries, fixing...")

                # Fix invalid geometries using buffer(0) trick
                # This is a standard GIS practice for fixing topology errors
                def fix_geometry(geom):
                    if geom is None or geom.is_empty:
                        return geom
                    if not geom.is_valid:
                        try:
                            # buffer(0) is a common technique to fix invalid geometries
                            fixed = geom.buffer(0)
                            if fixed.is_valid:
                                return fixed
                            # If still invalid, try make_valid (requires shapely 2.0+)
                            try:
                                from shapely import make_valid
                                return make_valid(geom)
                            except ImportError:
                                logger.warning("shapely.make_valid not available, using buffer(0) only")
                                return fixed
                        except Exception as e:
                            logger.error(f"Failed to fix geometry: {e}")
                            return geom
                    return geom

                gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].apply(fix_geometry)

                # Check if fixed
                still_invalid = ~gdf.geometry.is_valid
                fixed_count = invalid_count - still_invalid.sum()
                self.stats['invalid_fixed'] = fixed_count

                if fixed_count > 0:
                    logger.info(f"Fixed {fixed_count} invalid geometries")

                if still_invalid.any():
                    logger.warning(f"Could not fix {still_invalid.sum()} geometries, removing them")
                    gdf = gdf[~still_invalid].copy()

        # 3. Ensure correct CRS
        if gdf.crs is not None:
            current_crs = gdf.crs.to_string()
            if current_crs != target_crs:
                logger.info(f"Transforming CRS from {current_crs} to {target_crs}")
                gdf = gdf.to_crs(target_crs)
                self.stats['crs_transformed'] = True
        else:
            logger.warning("No CRS defined, setting to WGS84")
            gdf = gdf.set_crs(target_crs)
            self.stats['crs_transformed'] = True

        # 4. Remove duplicate geometries
        if remove_duplicates and len(gdf) > 0:
            # Use geometry WKT for duplicate detection
            before_dup_count = len(gdf)
            gdf = gdf.drop_duplicates(subset=['geometry']).copy()
            dup_count = before_dup_count - len(gdf)
            if dup_count > 0:
                self.stats['duplicates_removed'] = dup_count
                logger.info(f"Removed {dup_count} duplicate geometries")

        # 5. Ensure geometries are not too complex (reduce vertices if needed)
        # This is especially important for web display
        gdf = self._reduce_complexity(gdf)

        final_count = len(gdf)
        removed_total = original_count - final_count
        if removed_total > 0:
            logger.info(f"Cleaned: {original_count} -> {final_count} features ({removed_total} removed)")

        return gdf

    def _reduce_complexity(self, gdf: gpd.GeoDataFrame, max_vertices: int = 10000) -> gpd.GeoDataFrame:
        """
        Reduce geometry complexity for features with too many vertices
        This improves rendering performance significantly
        """
        def count_vertices(geom):
            if geom is None:
                return 0
            if isinstance(geom, (Polygon, MultiPolygon)):
                return len(geom.exterior.coords) if hasattr(geom, 'exterior') else sum(len(p.exterior.coords) for p in geom.geoms)
            return 0

        complex_mask = gdf.geometry.apply(lambda g: count_vertices(g) > max_vertices)
        complex_count = complex_mask.sum()

        if complex_count > 0:
            logger.info(f"Simplifying {complex_count} complex geometries...")
            # Use Douglas-Peucker simplification with tolerance
            gdf.loc[complex_mask, 'geometry'] = gdf.loc[complex_mask, 'geometry'].simplify(
                tolerance=0.0001,
                preserve_topology=True
            )

        return gdf

    def validate_and_report(self, gdf: gpd.GeoDataFrame) -> dict:
        """
        Validate GeoDataFrame and return detailed report

        Returns:
            Dictionary with validation results
        """
        report = {
            'total_features': len(gdf),
            'null_geometries': 0,
            'invalid_geometries': 0,
            'invalid_details': [],
            'crs': str(gdf.crs) if gdf.crs else 'None',
            'geometry_types': {},
            'bbox': None,
            'is_valid': True
        }

        if gdf.empty:
            report['is_valid'] = False
            return report

        # Count nulls
        null_mask = gdf.geometry.isna() | gdf.geometry.is_empty
        report['null_geometries'] = null_mask.sum()

        # Count invalids
        valid_gdf = gdf[~null_mask]
        if not valid_gdf.empty:
            invalid_mask = ~valid_gdf.geometry.is_valid
            report['invalid_geometries'] = invalid_mask.sum()

            # Get details of first few invalid geometries
            if report['invalid_geometries'] > 0:
                invalid_geoms = valid_gdf[invalid_mask].geometry.head(5)
                for idx, geom in enumerate(invalid_geoms):
                    report['invalid_details'].append({
                        'index': idx,
                        'reason': validation.explain_validity(geom)
                    })

        # Geometry types
        report['geometry_types'] = gdf.geometry.type.value_counts().to_dict()

        # Bounding box
        if not gdf.empty:
            bounds = gdf.total_bounds
            report['bbox'] = {
                'minx': float(bounds[0]),
                'miny': float(bounds[1]),
                'maxx': float(bounds[2]),
                'maxy': float(bounds[3])
            }

        # Overall validity
        report['is_valid'] = (
            report['null_geometries'] == 0 and
            report['invalid_geometries'] == 0 and
            report['crs'] is not None
        )

        return report

    def get_stats(self) -> dict:
        """Get cleaning statistics"""
        return self.stats.copy()


def clean_layer_file(
    input_path: Path,
    output_path: Optional[Path] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None
) -> bool:
    """
    Clean a GeoPackage file and save cleaned version

    Args:
        input_path: Path to input GeoPackage
        output_path: Path to output GeoPackage (if None, overwrites input)
        bbox: Optional bounding box to filter features

    Returns:
        True if successful
    """
    try:
        logger.info(f"Loading layer from {input_path}")

        # Load with bbox if provided
        if bbox:
            gdf = gpd.read_file(input_path, bbox=bbox, engine='pyogrio')
        else:
            gdf = gpd.read_file(input_path, engine='pyogrio')

        logger.info(f"Loaded {len(gdf)} features")

        # Clean geometries
        cleaner = GeometryCleaner()
        gdf_clean = cleaner.clean_geodataframe(gdf)

        # Validate
        report = cleaner.validate_and_report(gdf_clean)
        logger.info(f"Validation: {report}")

        # Save
        output = output_path or input_path
        logger.info(f"Saving cleaned layer to {output}")
        gdf_clean.to_file(output, driver='GPKG', engine='pyogrio')

        stats = cleaner.get_stats()
        logger.info(f"Cleaning stats: {stats}")

        return True

    except Exception as e:
        logger.error(f"Error cleaning layer: {e}", exc_info=True)
        return False
