"""
GeoPackage import endpoint for Orata API Backend.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.status import HTTP_201_CREATED
import os
import tempfile
import shutil
from app.crud import spatial as spatial_crud
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/geopackage/", status_code=HTTP_201_CREATED)
async def import_geopackage(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import a GeoPackage file, create a spatial table named after the file (without extension),
    and load its features into the database.
    """
    if not file.filename.lower().endswith('.gpkg'):
        raise HTTPException(status_code=400, detail="Only .gpkg files are supported.")

    table_name = os.path.splitext(os.path.basename(file.filename))[0]
    with tempfile.NamedTemporaryFile(delete=False, suffix='.gpkg') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # You should implement this function in app/crud/spatial.py
        # It should create the table and import features from the GeoPackage
        # The CRUD function will now handle the deletion of tmp_path
        spatial_crud.crud_spatial.import_geopackage_to_table(db, tmp_path, table_name)
    except Exception as e:
        # Don't remove tmp_path here anymore, it's handled in CRUD or might be needed for debugging
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    # Don't remove tmp_path here anymore, it's handled in CRUD
    return JSONResponse({"message": f"Imported {file.filename} as table '{table_name}'"}, status_code=HTTP_201_CREATED)
