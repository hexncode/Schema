"""
Atlas GIS Models - PostGIS-backed spatial data storage

These models store GIS data in PostgreSQL/PostGIS for efficient
spatial queries and database management via pgAdmin.
"""
from django.db import models
from django.conf import settings

# Only import GIS fields if PostGIS is enabled
if getattr(settings, 'USE_POSTGIS', False):
    from django.contrib.gis.db import models as gis_models
    GeometryField = gis_models.GeometryField
    PolygonField = gis_models.PolygonField
    MultiPolygonField = gis_models.MultiPolygonField
    PointField = gis_models.PointField
    GIS_ENABLED = True
else:
    # Fallback for SQLite - models won't have spatial capabilities
    GeometryField = None
    PolygonField = None
    MultiPolygonField = None
    PointField = None
    GIS_ENABLED = False


class GISLayerManager(models.Manager):
    """Custom manager for GIS layers with spatial queries"""

    def get_by_name(self, name):
        """Get layer by name (case-insensitive)"""
        return self.filter(name__iexact=name).first()

    def active_layers(self):
        """Get all active layers"""
        return self.filter(is_active=True)


class GISLayer(models.Model):
    """
    Metadata for GIS layers stored in the database.
    Each layer corresponds to a table of features.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default='General', db_index=True)

    # Source information
    source_file = models.CharField(max_length=500, blank=True, help_text="Original source file path")
    source_crs = models.CharField(max_length=50, default='EPSG:4283', help_text="Original coordinate reference system")

    # Display settings
    min_zoom = models.IntegerField(default=10)
    max_zoom = models.IntegerField(default=22)
    style_color = models.CharField(max_length=20, default='#3388ff')
    style_weight = models.FloatField(default=1.0)
    style_opacity = models.FloatField(default=0.7)
    style_fill_opacity = models.FloatField(default=0.2)

    # Status
    is_active = models.BooleanField(default=True)
    feature_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GISLayerManager()

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'GIS Layer'
        verbose_name_plural = 'GIS Layers'

    def __str__(self):
        return f"{self.display_name} ({self.feature_count} features)"


if GIS_ENABLED:
    class CadastralLot(gis_models.Model):
        """
        NSW Cadastral Lots - property boundaries
        ~3.3 million features from Lots.gpkg
        """
        # Core identifiers
        lot_id = models.CharField(max_length=50, db_index=True, blank=True, null=True)
        lot_number = models.CharField(max_length=20, blank=True, null=True)
        plan_number = models.CharField(max_length=30, blank=True, null=True)
        plan_label = models.CharField(max_length=50, blank=True, null=True)

        # Address information
        address = models.CharField(max_length=300, blank=True, null=True)

        # Area
        area_sqm = models.FloatField(null=True, blank=True, help_text="Area in square meters")

        # Administrative
        lga = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local Government Area")
        parish = models.CharField(max_length=100, blank=True, null=True)

        # Geometry - MultiPolygon to handle complex lot shapes
        geom = gis_models.MultiPolygonField(srid=4326, spatial_index=True)

        # Metadata
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            verbose_name = 'Cadastral Lot'
            verbose_name_plural = 'Cadastral Lots'
            indexes = [
                models.Index(fields=['lot_number', 'plan_number']),
                models.Index(fields=['lga']),
            ]

        def __str__(self):
            if self.lot_number and self.plan_number:
                return f"Lot {self.lot_number} {self.plan_number}"
            return self.lot_id or f"Lot #{self.pk}"


    class Suburb(gis_models.Model):
        """
        NSW Suburb/Locality boundaries
        ~15,000 features from Suburb.gpkg
        """
        # Identifiers
        suburb_name = models.CharField(max_length=100, db_index=True)
        postcode = models.CharField(max_length=10, blank=True, null=True, db_index=True)

        # Administrative
        lga = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local Government Area")
        state = models.CharField(max_length=10, default='NSW')

        # Area
        area_sqkm = models.FloatField(null=True, blank=True, help_text="Area in square kilometers")

        # Geometry
        geom = gis_models.MultiPolygonField(srid=4326, spatial_index=True)

        # Metadata
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            verbose_name = 'Suburb'
            verbose_name_plural = 'Suburbs'
            ordering = ['suburb_name']
            indexes = [
                models.Index(fields=['suburb_name', 'postcode']),
            ]

        def __str__(self):
            if self.postcode:
                return f"{self.suburb_name} {self.postcode}"
            return self.suburb_name


    class GenericFeature(gis_models.Model):
        """
        Generic feature storage for additional GIS layers.
        Flexible schema for various data types.
        """
        layer = models.ForeignKey(GISLayer, on_delete=models.CASCADE, related_name='features')

        # Flexible identifiers
        feature_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
        name = models.CharField(max_length=300, blank=True, null=True)

        # Store additional properties as JSON
        properties = models.JSONField(default=dict, blank=True)

        # Generic geometry field (can store any geometry type)
        geom = gis_models.GeometryField(srid=4326, spatial_index=True)

        # Metadata
        created_at = models.DateTimeField(auto_now_add=True)

        class Meta:
            verbose_name = 'Generic Feature'
            verbose_name_plural = 'Generic Features'
            indexes = [
                models.Index(fields=['layer', 'feature_id']),
            ]

        def __str__(self):
            return self.name or self.feature_id or f"Feature #{self.pk}"

else:
    # Placeholder models when PostGIS is not enabled
    # These won't have spatial capabilities but allow migrations to work

    class CadastralLot(models.Model):
        """Placeholder - enable PostGIS for full functionality"""
        lot_id = models.CharField(max_length=50, db_index=True, blank=True, null=True)
        lot_number = models.CharField(max_length=20, blank=True, null=True)
        plan_number = models.CharField(max_length=30, blank=True, null=True)

        class Meta:
            managed = False  # Don't create table in SQLite
            verbose_name = 'Cadastral Lot (PostGIS required)'

    class Suburb(models.Model):
        """Placeholder - enable PostGIS for full functionality"""
        suburb_name = models.CharField(max_length=100, db_index=True)
        postcode = models.CharField(max_length=10, blank=True, null=True)

        class Meta:
            managed = False
            verbose_name = 'Suburb (PostGIS required)'

    class GenericFeature(models.Model):
        """Placeholder - enable PostGIS for full functionality"""
        feature_id = models.CharField(max_length=100, blank=True, null=True)
        name = models.CharField(max_length=300, blank=True, null=True)

        class Meta:
            managed = False
            verbose_name = 'Generic Feature (PostGIS required)'
