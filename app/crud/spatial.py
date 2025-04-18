"""
CRUD operations for spatial features.
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

    def get(self, db: Session, feature_id: int, table_name: str) -> Optional[dict]:
        table_name = self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        sql = table.select().where(table.c.id == feature_id)
        row = db.execute(sql).fetchone()
        return dict(row._mapping) if row else None

    def get_multi(self, db: Session, table_name: str, skip: int = 0, limit: int = 100) -> list:
        table_name = self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        sql = table.select().offset(skip).limit(limit)
        rows = db.execute(sql).fetchall()
        return [dict(row._mapping) for row in rows]

    def create(self, db: Session, obj_in: SpatialCreate, table_name: str) -> dict:
        table_name = self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        try:
            geom_wkb = from_shape(shape(obj_in.geometry.model_dump()), srid=4326)
        except (GeometryTypeError, GEOSException, ValueError, TypeError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid geometry: {str(e)}")
        ins = table.insert().values(
            name=obj_in.name,
            description=obj_in.description,
            geometry=geom_wkb
        )
        result = db.execute(ins)
        db.commit()
        # Fetch the inserted row
        sel = table.select().where(table.c.id == result.inserted_primary_key[0])
        row = db.execute(sel).fetchone()
        return dict(row._mapping)

    def update(self, db: Session, db_obj: dict, obj_in: SpatialUpdate, table_name: str) -> dict:
        table_name = self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        update_data = {}
        if obj_in.name is not None:
            update_data['name'] = obj_in.name
        if obj_in.description is not None:
            update_data['description'] = obj_in.description
        if obj_in.geometry is not None:
            try:
                update_data['geometry'] = from_shape(shape(obj_in.geometry.model_dump()), srid=4326)
            except (GeometryTypeError, GEOSException, ValueError, TypeError) as e:
                raise HTTPException(status_code=422, detail=f"Invalid geometry: {str(e)}")
        upd = table.update().where(table.c.id == db_obj['id']).values(**update_data)
        db.execute(upd)
        db.commit()
        sel = table.select().where(table.c.id == db_obj['id'])
        row = db.execute(sel).fetchone()
        return dict(row._mapping)

    def remove(self, db: Session, feature_id: int, table_name: str) -> Optional[dict]:
        table_name = self._validate_table_name(table_name)
        table = self._get_table(db, table_name)
        sel = table.select().where(table.c.id == feature_id)
        row = db.execute(sel).fetchone()
        if not row:
            return None
        db.execute(table.delete().where(table.c.id == feature_id))
        db.commit()
        return dict(row._mapping)

crud_spatial = CRUDSpatial()
