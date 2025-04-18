"""
Pydantic schemas for spatial features.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any

from pydantic import model_validator

class GeometryBase(BaseModel):
    type: str = Field(..., description="Geometry type (e.g., Point, Polygon)")
    coordinates: Any = Field(..., description="Geometry coordinates in GeoJSON format.")

    @model_validator(mode="after")
    def validate_geometry(self):
        geom_type = self.type
        coords = self.coordinates
        if geom_type == "Point":
            if not (isinstance(coords, list) and len(coords) == 2 and all(isinstance(c, (int, float)) for c in coords)):
                raise ValueError("Point geometry must have two numeric coordinates")
        if geom_type == "Polygon":
            if not isinstance(coords, list) or not coords or not isinstance(coords[0], list):
                raise ValueError("Invalid Polygon coordinates")
            for ring in coords:
                if len(ring) < 4:
                    raise ValueError("Polygon ring must have at least 4 points")
                if ring[0] != ring[-1]:
                    raise ValueError("Polygon ring must be closed (first and last point must be the same)")
        if geom_type == "LineString":
            if not isinstance(coords, list) or len(coords) < 2:
                raise ValueError("LineString must have at least 2 points")
        if geom_type == "MultiPoint":
            if not isinstance(coords, list) or len(coords) < 1:
                raise ValueError("MultiPoint must have at least 1 point")
        if geom_type == "MultiLineString":
            if not isinstance(coords, list) or len(coords) < 1:
                raise ValueError("MultiLineString must have at least 1 LineString")
            for line in coords:
                if len(line) < 2:
                    raise ValueError("Each LineString in MultiLineString must have at least 2 points")
        if geom_type == "MultiPolygon":
            if not isinstance(coords, list) or len(coords) < 1:
                raise ValueError("MultiPolygon must have at least 1 Polygon")
            for poly in coords:
                if not isinstance(poly, list) or len(poly) < 1:
                    raise ValueError("Each Polygon in MultiPolygon must have at least 1 ring")
                for ring in poly:
                    if len(ring) < 4:
                        raise ValueError("Polygon ring in MultiPolygon must have at least 4 points")
                    if ring[0] != ring[-1]:
                        raise ValueError("Polygon ring in MultiPolygon must be closed (first and last point must be the same)")
        return self

class SpatialBase(BaseModel):
    name: str
    description: Optional[str] = None
    geometry: GeometryBase

class SpatialCreate(SpatialBase):
    pass

class SpatialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geometry: Optional[GeometryBase] = None

class SpatialOut(SpatialBase):
    id: int
    model_config = {"from_attributes": True}
