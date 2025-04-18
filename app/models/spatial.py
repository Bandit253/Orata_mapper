"""
Spatial model for all geometry types.
"""
from sqlalchemy import Column, String
from geoalchemy2 import Geometry
from app.models.base import BaseModel

class SpatialFeature(BaseModel):
    __tablename__ = "spatial_features"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False)
