"""
API endpoints for dynamic creation of spatial tables by geometry type.
"""
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from sqlalchemy import text
from app.db.session import engine

router = APIRouter()

class FieldDefinition(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$", description="Valid SQL column name")
    type: str = Field(..., description="Postgres data type, e.g., VARCHAR(255), INTEGER, DATE")
    nullable: Optional[bool] = True

class SpatialTableCreateRequest(BaseModel):
    table_name: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$", description="Valid SQL table name")
    geometry_type: Literal[
        "POINT", "LINESTRING", "POLYGON", "MULTIPOINT", "MULTILINESTRING", "MULTIPOLYGON"
    ]
    srid: int = 4326
    fields: Optional[List[FieldDefinition]] = Field(default_factory=list, description="Additional user-defined fields")

@router.post("/spatial-tables/", status_code=status.HTTP_201_CREATED)
def create_spatial_table(req: SpatialTableCreateRequest = Body(...)):
    """
    Create a new spatial table with the specified geometry type, SRID, and user-defined fields.
    """
    table_name = req.table_name.lower()
    geometry_type = req.geometry_type.upper()
    srid = req.srid
    # Reason: Prevent SQL injection by validating table_name and field names with regex/pattern
    field_sql = []
    for field in req.fields:
        nullable = "NULL" if field.nullable else "NOT NULL"
        field_sql.append(f"{field.name} {field.type} {nullable}")
    # Always include id, geometry
    columns = [
        "id SERIAL PRIMARY KEY",
        *field_sql,
        f"geometry geometry({geometry_type}, {srid}) NOT NULL"
    ]
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (" + ", ".join(columns) + ")"
    try:
        with engine.connect() as connection:
            connection.execute(text(sql))
            connection.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating table: {str(e)}")
    return {"message": f"Table '{table_name}' created with geometry type '{geometry_type}' and SRID {srid}."}

@router.get("/spatial-tables/", status_code=200)
def list_spatial_tables():
    """
    List all user-created spatial tables (with a geometry column).
    """
    sql = """
    SELECT table_name FROM information_schema.columns 
    WHERE udt_name = 'geometry' AND table_schema = 'public'
    """
    with engine.connect() as connection:
        result = connection.execute(text(sql))
        tables = [row[0] for row in result]
    return {"tables": tables}

@router.get("/spatial-tables/{table_name}", status_code=200)
def describe_spatial_table(table_name: str):
    """
    Describe the columns of a spatial table.
    """
    sql = text("""
        SELECT column_name, data_type, udt_name, is_nullable
        FROM information_schema.columns 
        WHERE table_name = :table_name AND table_schema = 'public'
    """)
    with engine.connect() as connection:
        result = connection.execute(sql, {"table_name": table_name})
        columns = [dict(row._mapping) for row in result]
    if not columns:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")
    return {"table": table_name, "columns": columns}

@router.delete("/spatial-tables/{table_name}", status_code=200)
def delete_spatial_table(table_name: str):
    """
    Drop a spatial table.
    """
    sql = text(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    try:
        with engine.connect() as connection:
            connection.execute(sql)
            connection.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting table: {str(e)}")
    return {"message": f"Table '{table_name}' deleted."}
