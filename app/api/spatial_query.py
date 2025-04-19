"""
Spatial query/filter endpoints for spatial_features table.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.db.session import SessionLocal, engine
from app.schemas.spatial import SpatialOut
from app.api.spatial import serialize_spatial_feature
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

# Patch: handle SQLAlchemy Row objects from raw SQL

def tuples_to_lists(obj):
    if isinstance(obj, tuple):
        return [tuples_to_lists(item) for item in obj]
    elif isinstance(obj, list):
        return [tuples_to_lists(item) for item in obj]
    else:
        return obj

def serialize_spatial_row(row):
    """
    Convert a SQLAlchemy Row/tuple/ORM object to a GeoJSON Feature dictionary.
    Handles ORM, Row, RowMapping results.
    Robustly serializes PostGIS geometry columns.
    Assumes 'id' and 'geometry' columns are present.
    Optional 'name' and 'description' columns are handled safely.
    """
    from geoalchemy2.elements import WKBElement, WKTElement
    from shapely.geometry.base import BaseGeometry
    from shapely import wkb

    # Use row._mapping for consistent access (works for ORM, Row, etc.)
    data = row._mapping if hasattr(row, '_mapping') else row # Handle potential plain dicts too

    # ID is assumed to exist after the import fix
    id_ = data.get('id')
    if id_ is None:
        # This shouldn't happen if the import worked, but good to check
        raise ValueError("Row is missing the mandatory 'id' column.")

    # Geometry is also mandatory
    geometry_col = data.get('geometry')
    if geometry_col is None:
         raise ValueError("Row is missing the mandatory 'geometry' column.")

    # Get optional fields safely
    name = data.get('name') # Defaults to None if missing
    description = data.get('description') # Defaults to None if missing

    # Now decode geometry_col robustly
    if isinstance(geometry_col, (WKBElement, WKTElement)):
        geom = mapping(to_shape(geometry_col))
    elif isinstance(geometry_col, BaseGeometry):
        geom = mapping(geometry_col)
    elif isinstance(geometry_col, (bytes, str)):
        # Raw WKB hex or bytes from DB
        if isinstance(geometry_col, str):
            # Assuming hex WKB representation if it's a string
            try:
                geom = mapping(wkb.loads(bytes.fromhex(geometry_col)))
            except (ValueError, TypeError): # Handle non-hex strings or bad WKB
                 raise ValueError(f"Cannot deserialize geometry from string: {geometry_col[:50]}...") # Show snippet
        else:
             # Assuming raw WKB bytes
            try:
                geom = mapping(wkb.loads(geometry_col))
            except (ValueError, TypeError): # Handle bad WKB
                 raise ValueError("Cannot deserialize geometry from bytes.")
    else:
        # Fallback: try to convert with to_shape, else raise
        try:
            geom = mapping(to_shape(geometry_col))
        except Exception as e:
            raise ValueError(f"Cannot serialize geometry: {e}")

    geom = tuples_to_lists(geom)

    # Build properties dict, excluding None values
    properties = {}
    if name is not None:
        properties['name'] = name
    if description is not None:
        properties['description'] = description
    # Add any other non-null properties here if needed in the future

    return {
        "type": "Feature",
        "id": id_,         # Use feature ID
        "geometry": geom,
        "properties": properties
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

@router.post("/features/{table_name}/query/bbox")
def query_bbox(
    table_name: str,
    body: dict = Body(..., description="Bounding box as {\"bbox\": [minx, miny, maxx, maxy]}"),
    db: Session = Depends(get_db)
):
    """
    Return all features within the bounding box from the specified table.
    Accepts either {\"bbox\": [...]} or direct dict with bbox key.
    Returns features as a GeoJSON FeatureCollection.
    """
    safe_table_name = validate_table_name(table_name)
    bbox = body.get("bbox")
    if not bbox or not isinstance(bbox, list) or len(bbox) != 4:
        raise HTTPException(status_code=422, detail="bbox must be a list of four numbers [minx, miny, maxx, maxy]")

    minx, miny, maxx, maxy = bbox

    # Fetch column names for the table
    try:
        column_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = :table_name
            ORDER BY ordinal_position;
        """)
        column_result = db.execute(column_query, {"table_name": safe_table_name})
        columns = [row[0] for row in column_result]

        if not columns:
            raise HTTPException(status_code=404, detail=f"Table '{safe_table_name}' not found or has no columns.")
        if 'id' not in columns:
             raise HTTPException(status_code=500, detail=f"Table '{safe_table_name}' is missing the required 'id' column.")
        if 'geometry' not in columns:
             raise HTTPException(status_code=500, detail=f"Table '{safe_table_name}' is missing the required 'geometry' column.")

    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Error fetching columns for table '{safe_table_name}': {e}")

    # Construct the SELECT statement with explicit, quoted column names
    select_columns = ", ".join([f'"{col}"' for col in columns]) # Quote identifiers

    # Construct the spatial query
    sql = text(f"""
        SELECT {select_columns}
        FROM public."{safe_table_name}" -- Use quoted table name
        WHERE geometry && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326)
    """)

    try:
        results = db.execute(sql, {"minx": minx, "miny": miny, "maxx": maxx, "maxy": maxy}).fetchall()
        features = [serialize_spatial_row(row) for row in results]
        # Return as GeoJSON FeatureCollection
        return {
            "type": "FeatureCollection",
            "features": features
        }
    except Exception as e:
        # Log the error e
        raise HTTPException(status_code=500, detail=f"Error querying features: {e}")

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
