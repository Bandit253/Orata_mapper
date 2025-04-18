"""
Spatial query/filter endpoints for spatial_features table.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.session import SessionLocal
from app.schemas.spatial import SpatialOut
from app.api.spatial import serialize_spatial_feature
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

# Patch: handle SQLAlchemy Row objects from raw SQL

def serialize_spatial_row(row):
    """
    Convert a SQLAlchemy Row/tuple/ORM object to a dict compatible with SpatialOut schema.
    Handles ORM, Row, RowMapping, and tuple results from raw SQL.
    Robustly serializes PostGIS geometry columns.
    """
    from geoalchemy2.elements import WKBElement, WKTElement
    from shapely.geometry.base import BaseGeometry
    from shapely import wkb
    from app.api.spatial import tuples_to_lists

    # Handle tuple result (raw SQL) by index
    if isinstance(row, tuple):
        # Assume column order: id, created_at, updated_at, name, description, geometry
        id_, _, _, name, description, geometry_col = row
    else:
        db_obj = row
        if hasattr(row, "_mapping"):
            db_obj = row._mapping
        id_ = db_obj["id"] if isinstance(db_obj, dict) else db_obj.id
        name = db_obj["name"] if isinstance(db_obj, dict) else db_obj.name
        description = db_obj.get("description") if isinstance(db_obj, dict) else db_obj.description
        geometry_col = db_obj["geometry"] if isinstance(db_obj, dict) else db_obj.geometry

    # Now decode geometry_col robustly
    if isinstance(geometry_col, (WKBElement, WKTElement)):
        geom = mapping(to_shape(geometry_col))
    elif isinstance(geometry_col, BaseGeometry):
        geom = mapping(geometry_col)
    elif isinstance(geometry_col, (bytes, str)):
        # Raw WKB hex or bytes from DB
        if isinstance(geometry_col, str):
            geom = mapping(wkb.loads(bytes.fromhex(geometry_col)))
        else:
            geom = mapping(wkb.loads(geometry_col))
    else:
        # Fallback: try to convert with to_shape, else raise
        try:
            geom = mapping(to_shape(geometry_col))
        except Exception as e:
            raise ValueError(f"Cannot serialize geometry: {e}")
    geom = tuples_to_lists(geom)
    return {
        "id": id_,
        "name": name,
        "description": description,
        "geometry": geom
    }

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import json

@router.post("/features/{table_name}/query/intersects", response_model=List[SpatialOut])
def query_intersects(
    table_name: str,
    geometry: dict = Body(..., description="GeoJSON geometry for intersection query"),
    db: Session = Depends(get_db)
):
    """
    Return all features that intersect the given geometry from the specified table.
    Accepts either a GeoJSON dict or {"geometry": geojson} (for compatibility with some clients/tests).
    """
    table_name = validate_table_name(table_name)
    if "geometry" in geometry and isinstance(geometry["geometry"], dict):
        geojson = geometry["geometry"]
    else:
        geojson = geometry
    geojson_str = json.dumps(geojson)
    sql = text(f"""
        SELECT * FROM {table_name}
        WHERE ST_Intersects(
            geometry,
            ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
        )
    """)
    try:
        results = db.execute(sql, {"geojson": geojson_str}).fetchall()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid geometry: {str(e)}")
    return [serialize_spatial_row(row) for row in results]

import re

def validate_table_name(table_name: str) -> str:
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise HTTPException(status_code=400, detail="Invalid table name")
    return table_name

@router.post("/features/{table_name}/query/within", response_model=List[SpatialOut])
def query_within(
    table_name: str,
    geometry: dict = Body(..., description="GeoJSON geometry for within query"),
    db: Session = Depends(get_db)
):
    """
    Return all features within the given geometry from the specified table.
    Accepts either a GeoJSON dict or {"geometry": geojson} (for compatibility with some clients/tests).
    """
    table_name = validate_table_name(table_name)
    if "geometry" in geometry and isinstance(geometry["geometry"], dict):
        geojson = geometry["geometry"]
    else:
        geojson = geometry
    geojson_str = json.dumps(geojson)
    sql = text(f"""
        SELECT * FROM {table_name}
        WHERE ST_Within(
            geometry,
            ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)
        )
    """)
    try:
        results = db.execute(sql, {"geojson": geojson_str}).fetchall()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid geometry: {str(e)}")
    return [serialize_spatial_row(row) for row in results]

@router.post("/features/{table_name}/query/bbox", response_model=List[SpatialOut])
def query_bbox(
    table_name: str,
    body: dict = Body(..., description="Bounding box as {\"bbox\": [minx, miny, maxx, maxy]}"),
    db: Session = Depends(get_db)
):
    """
    Return all features within the bounding box from the specified table.
    Accepts either {"bbox": [...]} or direct dict with bbox key.
    """
    table_name = validate_table_name(table_name)
    bbox = body.get("bbox") if isinstance(body, dict) else None
    if bbox is None and isinstance(body, dict) and len(body) == 4:
        bbox = [body.get(k) for k in ("minx", "miny", "maxx", "maxy")]
    if not bbox or not isinstance(bbox, list) or len(bbox) != 4:
        raise HTTPException(status_code=422, detail="bbox must be a list of four numbers [minx, miny, maxx, maxy]")
    minx, miny, maxx, maxy = bbox
    sql = text(f"""
        SELECT * FROM {table_name}
        WHERE geometry && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326)
    """)
    results = db.execute(sql, {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy}).fetchall()
    return [serialize_spatial_row(row) for row in results]

@router.post("/features/{table_name}/query/distance", response_model=List[SpatialOut])
def query_distance(
    table_name: str,
    geometry: dict = Body(..., description="GeoJSON geometry for distance query"),
    distance: float = Body(..., description="Distance in meters"),
    db: Session = Depends(get_db)
):
    """
    Return all features within a given distance (meters) of the geometry from the specified table.
    """
    table_name = validate_table_name(table_name)
    geojson_str = json.dumps(geometry)
    sql = text(f"""
        SELECT * FROM {table_name}
        WHERE ST_DWithin(
            geometry::geography,
            ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326)::geography,
            :distance
        )
    """)
    results = db.execute(sql, {"geojson": geojson_str, "distance": distance}).fetchall()
    return [serialize_spatial_row(row) for row in results]

import json

@router.post("/features/{table_name}/query/buffer", response_model=List[SpatialOut])
def query_buffer(
    table_name: str,
    geometry: dict = Body(..., description="GeoJSON geometry for buffer query"),
    buffer: float = Body(..., description="Buffer distance in meters"),
    db: Session = Depends(get_db)
):
    """
    Return all features that intersect the buffer around the given geometry from the specified table.
    """
    table_name = validate_table_name(table_name)
    geojson_str = json.dumps(geometry)
    sql = text(f"""
        SELECT * FROM {table_name}
        WHERE ST_Intersects(
            geometry,
            ST_Buffer(ST_SetSRID(ST_GeomFromGeoJSON(:geojson), 4326), :buffer)
        )
    """)
    try:
        results = db.execute(sql, {"geojson": geojson_str, "buffer": buffer}).fetchall()
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid geometry or buffer: {str(e)}")
    return [serialize_spatial_row(row) for row in results]
