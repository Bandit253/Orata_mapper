"""
FastAPI entrypoint for Orata API Backend.
"""
from fastapi import FastAPI
from app.api import spatial
from app.api import spatial_table
from app.api import spatial_query
from app.api import geopackage_import

app = FastAPI(
    title="Orata API Backend",
    description="A RESTful API for spatial and a-spatial data management.",
    version="0.1.0"
)

app.include_router(spatial.router)
app.include_router(spatial_table.router)
app.include_router(spatial_query.router)
app.include_router(geopackage_import.router)
