"""
CRUD operations for spatial features and GeoPackage import.
"""
from sqlalchemy.orm import Session
from app.models.spatial import SpatialFeature
from app.schemas.spatial import SpatialCreate, SpatialUpdate
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape, mapping
from typing import List, Optional
import re
from sqlalchemy import Table, MetaData, text
from fastapi import HTTPException
from shapely.errors import GeometryTypeError, GEOSException
import fiona
import sqlalchemy
from shapely import geometry as sgeom
from geoalchemy2 import WKBElement
import os

class CRUDSpatial:
    """
    CRUD utility for spatial features, supporting dynamic table names via reflection or raw SQL.
    """
    def _validate_table_name(self, table_name: str) -> str:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise HTTPException(status_code=400, detail="Invalid table name")
        return table_name

    def _get_table(self, db: Session, table_name: str):
        metadata = MetaData()
        try:
            table = Table(table_name, metadata, autoload_with=db.get_bind())
        except Exception:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' does not exist.")
        return table

    # ... (existing CRUD methods remain unchanged)

    def import_geopackage_to_table(self, db: Session, gpkg_path: str, table_name: str):
        """
        Import features from a GeoPackage file into a new spatial table.

        Args:
            db (Session): The database session.
            gpkg_path (str): Path to the temporary GeoPackage file.
            table_name (str): The desired name for the new database table.
        """
        # Validate table name
        self._validate_table_name(table_name)
        # Use GeoPandas for convenience
        import geopandas as gpd

        try:
            # Read directly using GeoPandas read_file
            # This handles opening and closing the file internally.
            # Assuming only one layer of interest (the first one)
            gdf = gpd.read_file(gpkg_path, layer=0)

            if gdf.empty:
                # Raise exception if the layer is empty, but don't delete yet
                raise ValueError("GeoPackage layer is empty or could not be read.")

            # Check if 'geometry' column exists, if not, try common alternatives or raise error
            if 'geometry' not in gdf.columns:
                # Attempt to find a geometry column based on common names or geometry type
                geom_col = None
                for col in gdf.columns:
                    # Check for GeoAlchemy's WKBElement or base Shapely geometry types
                    if isinstance(gdf[col].iloc[0], (WKBElement, sgeom.base.BaseGeometry)):
                        geom_col = col
                        break
                    elif col.lower() in ['geom', 'shape', 'the_geom']:
                        geom_col = col
                        break
                if geom_col:
                    gdf = gdf.set_geometry(geom_col)
                else:
                    raise ValueError("Could not automatically detect the geometry column. Please ensure your GeoPackage has a valid geometry column.")

            # Ensure geometry column is set correctly for to_postgis
            if not gdf.geometry.name == 'geometry':
                gdf = gdf.rename_geometry('geometry')

            # Write to PostGIS using the session's connection
            # Ensure an 'id' column is created from the index
            gdf.to_postgis(table_name, db.get_bind(), if_exists='replace', index=True, index_label='id')

        except fiona.errors.DriverError as e:
            # Catch Fiona driver errors (e.g., file not found, invalid format)
            raise HTTPException(status_code=400, detail=f"Error reading GeoPackage: {str(e)}")
        except ValueError as e:
            # Catch specific value errors we raised or from GDF processing
            raise HTTPException(status_code=400, detail=f"Data error: {str(e)}")
        except Exception as e:
            # Catch specific DB errors if needed or other general exceptions
            raise HTTPException(status_code=500, detail=f"Database write or processing failed: {str(e)}")
        finally:
            # Ensure the temporary file is deleted even if errors occurred
            if os.path.exists(gpkg_path):
                try:
                    os.remove(gpkg_path)
                except OSError as e:
                    # Log this error, but don't necessarily raise an exception
                    # as the main operation might have succeeded.
                    print(f"Warning: Could not remove temporary file {gpkg_path}: {e}")

crud_spatial = CRUDSpatial()
