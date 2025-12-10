"""
GIS Layer Manager
Auto-discovers .gpkg files and handles efficient loading with tiling
"""

import geopandas as gpd
import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from shapely.geometry import box
import warnings
import math

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


@dataclass
class LayerConfig:
    """Configuration for a single GIS layer"""
    name: str
    path: Path
    display_name: str
    category: str = "General"
    min_zoom: int = 10
    max_zoom: int = 21
    style: Dict[str, Any] = field(default_factory=dict)
    interactive: bool = True
    attributes: List[str] = field(default_factory=list)
    label_field: Optional[str] = None


class LayerManager:
    """Manages GIS layers with auto-discovery and efficient loading"""

    def __init__(self, layers_path: Path, metadata_file: Optional[Path] = None):
        """
        Initialize the layer manager

        Args:
            layers_path: Path to Layers directory (e.g., atlas/gis/Layers)
            metadata_file: Optional YAML file with layer metadata
        """
        self.layers_path = Path(layers_path)
        self.metadata_file = metadata_file or (self.layers_path.parent / 'layers.yaml')
        self.layers: Dict[str, LayerConfig] = {}
        self.settings = {
            'cache_ttl_minutes': 15,
            'cache_max_items': 100,
            'tile_size': 0.01,
            'default_min_zoom': 10
        }

        self._load_metadata()
        self._discover_layers()

        logger.info(f"LayerManager initialized with {len(self.layers)} layers")

    def _load_metadata(self):
        """Load metadata from YAML file if it exists"""
        if not self.metadata_file.exists():
            logger.info(f"No metadata file found at {self.metadata_file}, using defaults")
            return

        try:
            with open(self.metadata_file, 'r') as f:
                data = yaml.safe_load(f)

            # Load global settings
            if 'settings' in data:
                self.settings.update(data['settings'])

            # Store layer metadata for later use
            self._metadata = data.get('layers', {})
            logger.info(f"Loaded metadata for {len(self._metadata)} layers")

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            self._metadata = {}

    def _discover_layers(self):
        """Auto-discover all .gpkg files in the Layers directory"""
        if not self.layers_path.exists():
            logger.warning(f"Layers path does not exist: {self.layers_path}")
            return

        # Find all .gpkg files recursively
        gpkg_files = list(self.layers_path.rglob('*.gpkg'))
        logger.info(f"Found {len(gpkg_files)} .gpkg files")

        for gpkg_path in gpkg_files:
            # Get layer name from filename (without extension)
            layer_name = gpkg_path.stem

            # Get category from parent folder name
            category = gpkg_path.parent.name

            # Get metadata if available
            metadata = getattr(self, '_metadata', {}).get(layer_name, {})

            # Create layer config
            config = LayerConfig(
                name=layer_name,
                path=gpkg_path,
                display_name=metadata.get('display_name', layer_name.replace('_', ' ').title()),
                category=metadata.get('category', category),
                min_zoom=metadata.get('min_zoom', self.settings['default_min_zoom']),
                max_zoom=metadata.get('max_zoom', 21),
                style=metadata.get('style', {}),
                interactive=metadata.get('interactive', True),
                attributes=metadata.get('attributes', []),
                label_field=metadata.get('label_field')
            )

            self.layers[layer_name] = config
            logger.info(f"  {layer_name}: {gpkg_path} ({category})")

    def get_layer(self, name: str) -> Optional[LayerConfig]:
        """Get layer configuration by name"""
        return self.layers.get(name)

    def list_layers(self) -> List[LayerConfig]:
        """Get list of all available layers"""
        return list(self.layers.values())

    def load_layer(
        self,
        name: str,
        bbox: Tuple[float, float, float, float],
        zoom: int,
        simplify: bool = True
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Load layer data for given viewport

        Args:
            name: Layer name
            bbox: Bounding box (minx, miny, maxx, maxy)
            zoom: Current zoom level
            simplify: Whether to simplify geometries

        Returns:
            GeoDataFrame or None
        """
        layer = self.get_layer(name)
        if not layer:
            logger.error(f"Layer not found: {name}")
            return None

        # Check zoom level
        if zoom < layer.min_zoom or zoom > layer.max_zoom:
            logger.debug(f"Layer {name} not available at zoom {zoom}")
            return None

        try:
            # Load with pyogrio if available (faster)
            try:
                gdf = gpd.read_file(
                    layer.path,
                    bbox=bbox,
                    engine='pyogrio',
                    use_arrow=True
                )
            except (ImportError, Exception):
                # Fallback to fiona
                gdf = gpd.read_file(layer.path, bbox=bbox)

            if gdf.empty:
                return None

            # Ensure WGS84
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Keep only specified attributes if defined
            if layer.attributes:
                keep_cols = ['geometry'] + [col for col in layer.attributes if col in gdf.columns]
                gdf = gdf[keep_cols]

            # Simplify geometries based on zoom
            if simplify:
                tolerance = self._get_simplify_tolerance(zoom)
                if tolerance:
                    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=False)

            # NO FEATURE LIMITS - load ALL lots in tile
            # Small tile size (0.002 degrees) means each tile is manageable
            logger.debug(f"Loaded {len(gdf)} features for {name} at zoom {zoom}")

            return gdf

        except Exception as e:
            logger.error(f"Error loading layer {name}: {e}", exc_info=True)
            return None

    def _get_simplify_tolerance(self, zoom: int) -> Optional[float]:
        """Calculate simplification tolerance based on zoom level"""
        # More aggressive simplification at lower zooms
        tolerance_map = {
            10: 0.001,
            12: 0.0005,
            14: 0.0002,
            15: 0.0001,
            16: 0.00005,
            17: 0.00002,
            18: 0.00001,
            19: 0.000005,
            20: 0.000001
        }

        for z in sorted(tolerance_map.keys(), reverse=True):
            if zoom >= z:
                return tolerance_map[z]
        return None

    def layer_to_geojson(
        self,
        name: str,
        bbox: Tuple[float, float, float, float],
        zoom: int
    ) -> Optional[str]:
        """
        Load layer and convert to GeoJSON

        Args:
            name: Layer name
            bbox: Bounding box
            zoom: Zoom level

        Returns:
            GeoJSON string or None
        """
        gdf = self.load_layer(name, bbox, zoom)
        if gdf is None or gdf.empty:
            return None

        # Reduce precision for smaller file size
        from shapely import set_precision
        gdf['geometry'] = gdf['geometry'].apply(
            lambda geom: set_precision(geom, grid_size=0.000001)
        )

        return gdf.to_json(drop_id=True, show_bbox=False, na='drop')

    def generate_tiles(
        self,
        bbox: Tuple[float, float, float, float],
        tile_size: Optional[float] = None
    ) -> List[Dict]:
        """
        Generate tile grid for given bounding box

        Args:
            bbox: Bounding box (minx, miny, maxx, maxy)
            tile_size: Tile size in degrees (default from settings)

        Returns:
            List of tile dictionaries with id and bbox
        """
        minx, miny, maxx, maxy = bbox
        size = tile_size or self.settings['tile_size']

        # EXPAND bbox by 1 tile in all directions to catch partially visible lots
        # that start outside viewport but extend into it
        minx = minx - size
        miny = miny - size
        maxx = maxx + size
        maxy = maxy + size

        tiles = []

        # Calculate number of tiles
        nx = math.ceil((maxx - minx) / size)
        ny = math.ceil((maxy - miny) / size)

        for i in range(nx):
            for j in range(ny):
                tile_minx = minx + i * size
                tile_miny = miny + j * size
                tile_maxx = min(tile_minx + size, maxx)
                tile_maxy = min(tile_miny + size, maxy)

                tile_id = f"{i}_{j}"
                tiles.append({
                    'id': tile_id,
                    'bbox': (tile_minx, tile_miny, tile_maxx, tile_maxy),
                    'bbox_str': f"{tile_minx},{tile_miny},{tile_maxx},{tile_maxy}"
                })

        return tiles

    def query_at_point(
        self,
        name: str,
        lon: float,
        lat: float,
        buffer: float = 0.0001
    ) -> Optional[gpd.GeoDataFrame]:
        """
        Query features at a point

        Args:
            name: Layer name
            lon: Longitude
            lat: Latitude
            buffer: Buffer in degrees

        Returns:
            GeoDataFrame with features containing the point
        """
        bbox = (lon - buffer, lat - buffer, lon + buffer, lat + buffer)
        gdf = self.load_layer(name, bbox, zoom=20, simplify=False)

        if gdf is None or gdf.empty:
            return None

        from shapely.geometry import Point
        point = Point(lon, lat)

        contains = gdf['geometry'].contains(point)
        result = gdf[contains]

        return result if not result.empty else None
