"""
FastAPI entrypoint for PostGIS REST API Backend.
"""
from fastapi import FastAPI
from app.api import spatial
from app.api import spatial_table
from app.api import spatial_query

app = FastAPI(
    title="PostGIS REST API Backend",
    description="A RESTful API for spatial and a-spatial data management.",
    version="0.1.0"
)

app.include_router(spatial.router)
app.include_router(spatial_table.router)
app.include_router(spatial_query.router)
