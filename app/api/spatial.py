"""
Spatial API router for CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import SessionLocal
from app.schemas.spatial import SpatialCreate, SpatialUpdate, SpatialOut
from app.crud.spatial import crud_spatial

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

# ... (rest of imports and router setup)


def tuples_to_lists(obj):
    if isinstance(obj, tuple):
        return [tuples_to_lists(i) for i in obj]
    if isinstance(obj, list):
        return [tuples_to_lists(i) for i in obj]
    if isinstance(obj, dict):
        return {k: tuples_to_lists(v) for k, v in obj.items()}
    return obj

def serialize_spatial_feature(db_obj):
    """
    Convert a SpatialFeature SQLAlchemy object, dict, or any compatible object to a dict for SpatialOut schema.
    Handles dicts (dynamic table), ORM objects, and namedtuples.
    """
    # Defensive: try dict, then attribute, then fallback
    def get(field):
        if isinstance(db_obj, dict):
            return db_obj.get(field)
        if hasattr(db_obj, field):
            return getattr(db_obj, field)
        # fallback for namedtuple or rowproxy
        try:
            return db_obj[field]
        except Exception:
            return None
    geometry = get("geometry")
    id_ = get("id")
    name = get("name")
    description = get("description")
    geom = mapping(to_shape(geometry))
    geom = tuples_to_lists(geom)
    return {
        "id": id_,
        "name": name,
        "description": description,
        "geometry": geom,
    }

import re

def validate_table_name(table_name: str) -> str:
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")
    return table_name

@router.post("/features/{table_name}/", response_model=SpatialOut, status_code=status.HTTP_201_CREATED)
def create_feature(table_name: str, feature: SpatialCreate, db: Session = Depends(get_db)):
    """
    Create a new spatial feature in the specified table.
    """
    table_name = validate_table_name(table_name)
    db_obj = crud_spatial.create(db, feature, table_name=table_name)
    return serialize_spatial_feature(db_obj)

@router.get("/features/{table_name}/", response_model=List[SpatialOut])
def read_features(table_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List spatial features in the specified table.
    """
    table_name = validate_table_name(table_name)
    db_objs = crud_spatial.get_multi(db, table_name=table_name, skip=skip, limit=limit)
    return [serialize_spatial_feature(obj) for obj in db_objs]

@router.get("/features/{table_name}/{feature_id}", response_model=SpatialOut)
def read_feature(table_name: str, feature_id: int, db: Session = Depends(get_db)):
    """
    Get a spatial feature by ID from the specified table.
    """
    table_name = validate_table_name(table_name)
    db_obj = crud_spatial.get(db, feature_id, table_name=table_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    return serialize_spatial_feature(db_obj)

@router.put("/features/{table_name}/{feature_id}", response_model=SpatialOut)
def update_feature(table_name: str, feature_id: int, feature: SpatialUpdate, db: Session = Depends(get_db)):
    """
    Update a spatial feature in the specified table.
    """
    table_name = validate_table_name(table_name)
    db_obj = crud_spatial.get(db, feature_id, table_name=table_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    updated = crud_spatial.update(db, db_obj, feature, table_name=table_name)
    return serialize_spatial_feature(updated)

@router.delete("/features/{table_name}/{feature_id}", response_model=SpatialOut)
def delete_feature(table_name: str, feature_id: int, db: Session = Depends(get_db)):
    """
    Delete a spatial feature from the specified table.
    """
    table_name = validate_table_name(table_name)
    db_obj = crud_spatial.remove(db, feature_id, table_name=table_name)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Feature not found")
    return serialize_spatial_feature(db_obj)
