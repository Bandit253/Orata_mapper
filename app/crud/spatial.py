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

    def create(self, db: Session, feature: 'SpatialCreate', table_name: str):
        """
        Insert a new spatial feature into the specified table.

        Args:
            db (Session): Database session.
            feature (SpatialCreate): Feature to insert.
            table_name (str): Table name.

        Returns:
            Any: Inserted row as SQLAlchemy Row or ORM object.
        """
        self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        # Prepare geometry
        try:
            geom_shape = shape(feature.geometry.model_dump())
            geom_wkb = from_shape(geom_shape, srid=4326)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid geometry: {e}")
        # Prepare insert dict
        insert_dict = {
            'geometry': geom_wkb
        }
        if feature.name is not None:
            insert_dict['name'] = feature.name
        if feature.description is not None:
            insert_dict['description'] = feature.description
        try:
            insert_stmt = table.insert().values(**insert_dict).returning(table)
            result = db.execute(insert_stmt)
            db.commit()
            return result.fetchone()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database insert failed: {e}")

    def get(self, db: Session, feature_id: int, table_name: str):
        """
        Get a spatial feature by ID from the specified table.

        Args:
            db (Session): Database session.
            feature_id (int): Feature ID.
            table_name (str): Table name.

        Returns:
            Any: Row or ORM object, or None if not found.
        """
        self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        try:
            stmt = table.select().where(table.c.id == feature_id)
            result = db.execute(stmt)
            return result.fetchone()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database select failed: {e}")

    def get_multi(self, db: Session, table_name: str, skip: int = 0, limit: int = 100):
        """
        Get multiple spatial features from the specified table.

        Args:
            db (Session): Database session.
            table_name (str): Table name.
            skip (int): Offset.
            limit (int): Limit.

        Returns:
            List[Any]: List of rows or ORM objects.
        """
        self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        try:
            stmt = table.select().offset(skip).limit(limit)
            result = db.execute(stmt)
            return result.fetchall()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database select failed: {e}")

    def update(self, db: Session, db_obj: any, feature: 'SpatialUpdate', table_name: str):
        """
        Update a spatial feature in the specified table.

        Args:
            db (Session): Database session.
            db_obj (Any): Existing row/ORM object.
            feature (SpatialUpdate): Data to update.
            table_name (str): Table name.

        Returns:
            Any: Updated row or ORM object.
        """
        import logging
        logger = logging.getLogger("crud.spatial.update")
        self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        # If db_obj is a SQLAlchemy Row, convert to dict-like for key access
        if hasattr(db_obj, "_mapping"):
            db_obj = db_obj._mapping
        logger.info(f"Updating feature in table: {table_name}, feature_id: {db_obj['id']}")
        logger.debug(f"Incoming update data: {feature}")
        update_dict = {}
        if feature.name is not None:
            update_dict['name'] = feature.name
        if feature.description is not None:
            update_dict['description'] = feature.description
        if feature.geometry is not None:
            try:
                logger.debug(f"Raw geometry for update: {feature.geometry}")
                geom_shape = shape(feature.geometry.model_dump())
                geom_wkb = from_shape(geom_shape, srid=4326)
                update_dict['geometry'] = geom_wkb
            except Exception as e:
                logger.error(f"Invalid geometry in update: {e}")
                raise HTTPException(status_code=422, detail=f"Invalid geometry: {e}")
        logger.info(f"Update dict to apply: {update_dict}")
        if not update_dict:
            logger.warning("Update called with no fields to update.")
            raise HTTPException(status_code=400, detail="No fields to update.")
        try:
            stmt = (
                table.update()
                .where(table.c.id == db_obj['id'])
                .values(**update_dict)
                .returning(table)
            )
            logger.debug(f"Executing update statement: {stmt}")
            result = db.execute(stmt)
            db.commit()
            logger.info("Update successful.")
            return result.fetchone()
        except Exception as e:
            logger.error(f"Exception during update: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database update failed: {e}")

    def remove(self, db: Session, feature_id: int, table_name: str):
        """
        Delete a spatial feature by ID from the specified table.

        Args:
            db (Session): Database session.
            feature_id (int): Feature ID.
            table_name (str): Table name.

        Returns:
            Any: Deleted row or ORM object, or None if not found.
        """
        self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        try:
            stmt = table.delete().where(table.c.id == feature_id).returning(table)
            result = db.execute(stmt)
            db.commit()
            return result.fetchone()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Database delete failed: {e}")


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
