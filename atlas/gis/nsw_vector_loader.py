"""
NSW Vector Layer Loader
Optimized loading for large NSW GeoPackage datasets (Lots and Buildings)
with zoom-based filtering and efficient viewport-based queries
"""

import geopandas as gpd
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple, List
from shapely.geometry import box
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class NSWVectorLoader:
    """
    Optimized loader for NSW vector layers (Lots and Buildings)
    Implements zoom-based loading and viewport filtering for performance
    """

    def __init__(self, layers_base_path: Path):
        """
        Initialize the NSW Vector Loader

        Args:
            layers_base_path: Base path to the Layers folder (app/gis/Layers)
        """
        self.layers_base_path = layers_base_path
        self.nsw_path = layers_base_path / 'NSW'

        # Define layer configurations
        self.layers = {
            'nsw_lots': {
                'path': self.nsw_path / 'Lots.gpkg',
                'display_name': 'NSW Property Lots',
                'description': 'NSW property lot boundaries',
                'min_zoom': 15,  # Only load at zoom 15+
                'max_features': None,  # No limit - load ALL lots in viewport
                'simplify_tolerance': {
                    15: 0.0001,  # Aggressive simplification at zoom 15
                    16: 0.00005,
                    17: 0.00002,
                    18: 0.00001,
                    19: 0.000005,
                    20: 0.000001
                },
                'style': {
                    'color': '#2c3e50',
                    'weight': 1.5,
                    'fillColor': '#ecf0f1',
                    'fillOpacity': 0.1,
                    'opacity': 0.8
                }
            },
            'nsw_buildings': {
                'path': self.nsw_path / 'BLD_GreaterSydney.gpkg',
                'display_name': 'Greater Sydney Buildings',
                'description': 'Building footprints for Greater Sydney region',
                'min_zoom': 17,  # Raised to zoom 17+ for performance
                'max_features': 1000,  # Reduced for faster loading
                'simplify_tolerance': {
                    17: 0.00002,  # Heavy simplification
                    18: 0.00001,
                    19: 0.000005,
                    20: 0.000001
                },
                'style': {
                    'color': '#34495e',
                    'weight': 0.5,
                    'fillColor': '#bdc3c7',
                    'fillOpacity': 0.5
                }
            },
            'suburb': {
                'path': self.nsw_path / 'Suburb.gpkg',
                'display_name': 'NSW Suburbs',
                'description': 'NSW suburb boundaries',
                'min_zoom': 10,  # Load at zoom 10+ for suburb level
                'max_features': None,  # Load all suburbs in viewport
                'simplify_tolerance': {
                    10: 0.001,  # Simplification for lower zooms
                    12: 0.0005,
                    14: 0.0002,
                    16: 0.0001,
                    18: 0.00005
                },
                'style': {
                    'color': '#3498db',
                    'weight': 2,
                    'fillColor': '#3498db',
                    'fillOpacity': 0.05,
                    'opacity': 0.8
                }
            }
        }

    def should_load_layer(self, layer_name: str, zoom_level: int) -> bool:
        """
        Check if a layer should be loaded at the given zoom level

        Args:
            layer_name: Name of the layer (nsw_lots or nsw_buildings)
            zoom_level: Current map zoom level

        Returns:
            True if layer should be loaded, False otherwise
        """
        if layer_name not in self.layers:
            return False

        layer_config = self.layers[layer_name]
        return zoom_level >= layer_config['min_zoom']

    def load_layer(
        self,
        layer_name: str,
        bbox: Tuple[float, float, float, float],
        zoom_level: int,
        max_features: Optional[int] = None,
        clean_geometries: bool = True
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Load a layer with viewport and zoom-based filtering

        Args:
            layer_name: Name of the layer to load
            bbox: Bounding box (minx, miny, maxx, maxy) in EPSG:4326
            zoom_level: Current zoom level
            max_features: Override default max features limit
            clean_geometries: Apply geometry cleaning and validation

        Returns:
            GeoDataFrame with filtered features, or None if not available
        """
        # Check if layer exists
        if layer_name not in self.layers:
            logger.error(f"Layer '{layer_name}' not found")
            return None

        layer_config = self.layers[layer_name]

        # Check zoom level
        if not self.should_load_layer(layer_name, zoom_level):
            logger.debug(f"Layer '{layer_name}' not available at zoom level {zoom_level} (min: {layer_config['min_zoom']})")
            return None

        # Check if file exists
        layer_path = layer_config['path']
        if not layer_path.exists():
            logger.error(f"Layer file not found: {layer_path}")
            return None

        try:
            # Load with bounding box filter for efficiency
            # This reads only features that intersect the viewport
            # Try using pyogrio with Arrow for fastest performance
            try:
                gdf = gpd.read_file(
                    layer_path,
                    bbox=bbox,
                    engine='pyogrio',  # Faster than fiona
                    use_arrow=True,  # Use Apache Arrow for faster I/O
                    fid_as_index=True  # Use feature ID as index for better performance
                )
            except (ImportError, AttributeError, Exception) as e:
                # Fallback to fiona if pyogrio is not available or fails
                logger.warning(f"pyogrio failed ({str(e)}), falling back to fiona")
                gdf = gpd.read_file(
                    layer_path,
                    bbox=bbox
                )

            # If no features in viewport, return None
            if gdf.empty:
                return None

            # OPTIMIZATION: Clean and validate geometries if requested
            if clean_geometries:
                # Remove null/empty geometries
                null_mask = gdf.geometry.isna() | gdf.geometry.is_empty
                if null_mask.any():
                    gdf = gdf[~null_mask].copy()
                    if gdf.empty:
                        return None

                # Fix invalid geometries using buffer(0) - standard GIS practice
                invalid_mask = ~gdf.geometry.is_valid
                if invalid_mask.any():
                    logger.debug(f"Fixing {invalid_mask.sum()} invalid geometries in {layer_name}")
                    gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].buffer(0)

            # Ensure CRS is WGS84 (EPSG:4326)
            # Source data is EPSG:4283 (GDA94)
            if gdf.crs is not None:
                current_epsg = gdf.crs.to_epsg()
                if current_epsg != 4326:
                    logger.debug(f"Transforming {layer_name} from EPSG:{current_epsg} to EPSG:4326")
                    gdf = gdf.to_crs(epsg=4326)

            # OPTIMIZATION: Drop unnecessary columns BEFORE simplification to reduce memory
            if layer_name == 'nsw_lots':
                essential_cols = ['geometry', 'lotnumber', 'plannumber', 'planlabel',
                                'address', 'planlotare', 'planlota00', 'lganame', 'councilnam']
                # Keep only columns that exist
                keep_cols = [col for col in essential_cols if col in gdf.columns]
                gdf = gdf[keep_cols].copy()

            elif layer_name == 'nsw_buildings':
                # Buildings only need geometry for display
                gdf = gdf[['geometry']].copy()

            # OPTIMIZATION: Apply zoom-based simplification for performance
            # This reduces file size and improves rendering speed significantly
            simplify_tolerance = self._get_simplify_tolerance(layer_name, zoom_level)
            if simplify_tolerance is not None and simplify_tolerance > 0:
                # Use preserve_topology=False for faster simplification
                # This is acceptable for display purposes at web zoom levels
                gdf['geometry'] = gdf['geometry'].simplify(
                    simplify_tolerance,
                    preserve_topology=False
                )

            # OPTIMIZATION: Limit features to prevent browser overload
            max_feat = max_features or layer_config['max_features']
            if max_feat is not None and len(gdf) > max_feat:
                original_count = len(gdf)
                # Use spatial prioritization: keep features closest to bbox center
                bbox_center_x = (bbox[0] + bbox[2]) / 2
                bbox_center_y = (bbox[1] + bbox[3]) / 2

                # Calculate distance from center for prioritization
                gdf['_dist'] = gdf.geometry.centroid.apply(
                    lambda p: ((p.x - bbox_center_x)**2 + (p.y - bbox_center_y)**2)**0.5
                )
                gdf = gdf.nsmallest(max_feat, '_dist').drop(columns=['_dist'])

                logger.info(f"Limited {layer_name} to {max_feat} features (found {original_count}, prioritized by distance from center)")

            return gdf

        except Exception as e:
            logger.error(f"Error loading layer '{layer_name}': {str(e)}", exc_info=True)
            return None

    def _get_simplify_tolerance(self, layer_name: str, zoom_level: int) -> Optional[float]:
        """Get simplification tolerance for given layer and zoom level"""
        layer_config = self.layers[layer_name]
        tolerance_map = layer_config.get('simplify_tolerance', {})

        # Find the closest zoom level tolerance
        available_zooms = sorted(tolerance_map.keys())
        for z in reversed(available_zooms):
            if zoom_level >= z:
                return tolerance_map[z]

        return None

    def layer_to_geojson(
        self,
        layer_name: str,
        bbox: Tuple[float, float, float, float],
        zoom_level: int,
        max_features: Optional[int] = None,
        precision: int = 6
    ) -> Optional[str]:
        """
        Load a layer and convert to GeoJSON string with optimizations

        Args:
            layer_name: Name of the layer
            bbox: Bounding box (minx, miny, maxx, maxy)
            zoom_level: Current zoom level
            max_features: Max features to return
            precision: Decimal precision for coordinates (default: 6 = ~10cm)

        Returns:
            GeoJSON string or None
        """
        gdf = self.load_layer(layer_name, bbox, zoom_level, max_features)

        if gdf is None or gdf.empty:
            return None

        # OPTIMIZATION: Reduce coordinate precision based on zoom level
        # Higher zoom = more precision needed
        # This reduces file size by 30-50% and improves parsing/rendering speed
        if zoom_level >= 18:
            precision = 7  # ~1cm for high zoom
        elif zoom_level >= 16:
            precision = 6  # ~10cm for medium zoom
        else:
            precision = 5  # ~1m for low zoom

        # Apply precision reduction using shapely's set_precision
        # This snaps coordinates to a grid, reducing file size
        try:
            from shapely import set_precision
            grid_size = 10 ** (-precision)
            gdf['geometry'] = gdf['geometry'].apply(
                lambda geom: set_precision(geom, grid_size=grid_size) if geom is not None else geom
            )
        except Exception as e:
            logger.warning(f"Precision reduction failed: {e}, using original geometries")

        # OPTIMIZATION: Use compact JSON encoding
        # - drop_id: Don't include feature IDs (not needed for display)
        # - show_bbox: Don't include bounding boxes (redundant)
        # - na='drop': Remove null attribute values
        return gdf.to_json(drop_id=True, show_bbox=False, na='drop')

    def get_layer_info(self, layer_name: str) -> Optional[Dict]:
        """
        Get information about a layer

        Args:
            layer_name: Name of the layer

        Returns:
            Dictionary with layer metadata
        """
        if layer_name not in self.layers:
            return None

        layer_config = self.layers[layer_name]

        return {
            'name': layer_name,
            'display_name': layer_config['display_name'],
            'description': layer_config['description'],
            'min_zoom': layer_config['min_zoom'],
            'max_features': layer_config['max_features'],
            'style': layer_config['style'],
            'exists': layer_config['path'].exists(),
            'path': str(layer_config['path'])
        }

    def get_available_layers(self) -> List[str]:
        """
        Get list of available layers that exist on disk

        Returns:
            List of layer names
        """
        return [
            name for name, config in self.layers.items()
            if config['path'].exists()
        ]

    def query_features_at_point(
        self,
        layer_name: str,
        lon: float,
        lat: float,
        buffer: float = 0.0001
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Query features at a specific point

        Args:
            layer_name: Name of the layer
            lon: Longitude
            lat: Latitude
            buffer: Buffer distance in degrees (default ~10m)

        Returns:
            GeoDataFrame with matching features
        """
        # Create bounding box around point
        bbox = (lon - buffer, lat - buffer, lon + buffer, lat + buffer)

        # Load features in the area
        # Use high zoom level to ensure loading
        gdf = self.load_layer(layer_name, bbox, zoom_level=20)

        if gdf is None or gdf.empty:
            return None

        # Filter to features that actually contain the point
        from shapely.geometry import Point
        point = Point(lon, lat)

        # Check which features contain the point
        contains = gdf['geometry'].contains(point)
        result = gdf[contains]

        return result if not result.empty else None

    def get_layer_bounds(self, layer_name: str) -> Optional[Dict]:
        """
        Get the bounding box of a layer (full extent)
        Note: This can be slow for large datasets

        Args:
            layer_name: Name of the layer

        Returns:
            Dict with 'minx', 'miny', 'maxx', 'maxy' or None
        """
        if layer_name not in self.layers:
            return None

        layer_path = self.layers[layer_name]['path']
        if not layer_path.exists():
            return None

        try:
            # Read just the bounds without loading all features
            import fiona
            with fiona.open(layer_path) as src:
                bounds = src.bounds

            return {
                'minx': float(bounds[0]),
                'miny': float(bounds[1]),
                'maxx': float(bounds[2]),
                'maxy': float(bounds[3])
            }
        except Exception as e:
            logger.error(f"Error getting bounds for '{layer_name}': {str(e)}", exc_info=True)
            return None
