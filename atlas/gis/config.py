"""
GIS Layer Configuration and Metadata
Simplified configuration for NSW vector layers only
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Base path for GIS data
GIS_BASE_PATH = Path(__file__).parent
LAYERS_PATH = GIS_BASE_PATH / 'Layers'

@dataclass
class LayerMetadata:
    """Metadata for a GIS layer"""
    name: str
    path: str
    layer_type: str  # 'vector' or 'raster'
    format: str  # 'gpkg', etc.
    category: str  # Main category
    subcategory: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    visible_by_default: bool = False
    min_zoom: Optional[int] = None
    max_zoom: Optional[int] = None
    style: Dict = field(default_factory=dict)
    attributes: List[str] = field(default_factory=list)

    @property
    def full_path(self) -> Path:
        """Get absolute path to the layer file"""
        return Path(self.path)

    def exists(self) -> bool:
        """Check if layer file exists"""
        return self.full_path.exists()


class GISLayerCatalog:
    """Catalog of all available GIS layers organized by category"""

    def __init__(self):
        self.layers: Dict[str, LayerMetadata] = {}
        self._initialize_layers()

    def _initialize_layers(self):
        """Initialize all layer definitions"""

        # NSW Cadastral Lots
        nsw_lots_gpkg = LAYERS_PATH / 'NSW' / 'Lots.gpkg'
        if nsw_lots_gpkg.exists():
            self.add_layer(LayerMetadata(
                name='nsw_lots',
                path=str(nsw_lots_gpkg),
                layer_type='vector',
                format='gpkg',
                category='NSW',
                subcategory='Cadastral',
                display_name='NSW Property Lots',
                description='NSW property lot boundaries',
                visible_by_default=False,
                min_zoom=15,
                style={
                    'color': '#2c3e50',
                    'weight': 1.5,
                    'fillColor': '#ecf0f1',
                    'fillOpacity': 0.1,
                    'opacity': 0.8
                }
            ))

        # Greater Sydney Buildings
        nsw_buildings_gpkg = LAYERS_PATH / 'NSW' / 'BLD_GreaterSydney.gpkg'
        if nsw_buildings_gpkg.exists():
            self.add_layer(LayerMetadata(
                name='nsw_buildings',
                path=str(nsw_buildings_gpkg),
                layer_type='vector',
                format='gpkg',
                category='NSW',
                subcategory='Buildings',
                display_name='Greater Sydney Buildings',
                description='Building footprints for Greater Sydney region',
                visible_by_default=False,
                min_zoom=16,
                style={
                    'color': '#34495e',
                    'weight': 1,
                    'fillColor': '#bdc3c7',
                    'fillOpacity': 0.7
                }
            ))

        # Suburb Layer
        suburb_gpkg = LAYERS_PATH / 'NSW' / 'Suburb.gpkg'
        if suburb_gpkg.exists():
            self.add_layer(LayerMetadata(
                name='suburb',
                path=str(suburb_gpkg),
                layer_type='vector',
                format='gpkg',
                category='NSW',
                subcategory='Boundaries',
                display_name='NSW Suburbs',
                description='NSW suburb boundaries',
                visible_by_default=False,
                min_zoom=10,
                style={
                    'color': '#3498db',
                    'weight': 2,
                    'fillColor': '#3498db',
                    'fillOpacity': 0.05,
                    'opacity': 0.8
                }
            ))

    def add_layer(self, layer: LayerMetadata):
        """Add a layer to the catalog"""
        self.layers[layer.name] = layer

    def get_layer(self, name: str) -> Optional[LayerMetadata]:
        """Get a layer by name"""
        return self.layers.get(name)

    def get_layers_by_category(self, category: str) -> List[LayerMetadata]:
        """Get all layers in a category"""
        return [layer for layer in self.layers.values() if layer.category == category]

    def get_layers_by_subcategory(self, category: str, subcategory: str) -> List[LayerMetadata]:
        """Get all layers in a subcategory"""
        return [
            layer for layer in self.layers.values()
            if layer.category == category and layer.subcategory == subcategory
        ]

    def get_all_categories(self) -> List[str]:
        """Get list of all categories"""
        return sorted(list(set(layer.category for layer in self.layers.values())))

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a category"""
        subcats = set(
            layer.subcategory for layer in self.layers.values()
            if layer.category == category and layer.subcategory is not None
        )
        return sorted(list(subcats))

    def get_available_layers(self) -> List[LayerMetadata]:
        """Get all layers that exist on disk"""
        return [layer for layer in self.layers.values() if layer.exists()]

    def to_dict(self) -> Dict:
        """Export catalog as dictionary"""
        return {
            'categories': self.get_all_categories(),
            'layers': {
                name: {
                    'name': layer.name,
                    'display_name': layer.display_name,
                    'category': layer.category,
                    'subcategory': layer.subcategory,
                    'description': layer.description,
                    'visible_by_default': layer.visible_by_default,
                    'min_zoom': layer.min_zoom,
                    'max_zoom': layer.max_zoom,
                    'style': layer.style,
                    'exists': layer.exists()
                }
                for name, layer in self.layers.items()
            }
        }


# Global catalog instance
catalog = GISLayerCatalog()
