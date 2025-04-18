"""
Unit tests for spatial table creation endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("table_name, geometry_type, expected_status, fields", [
    ("test_points", "POINT", 201, []),
    ("test_lines", "LINESTRING", 201, []),
    ("test_polygons", "POLYGON", 201, [
        {"name": "label", "type": "VARCHAR(100)", "nullable": False},
        {"name": "created_at", "type": "DATE", "nullable": True},
    ]),
    ("bad-table-name!", "POINT", 422, []),  # Invalid table name
    ("test_points", "INVALIDTYPE", 422, []),  # Invalid geometry type
])
def test_create_spatial_table(table_name, geometry_type, expected_status, fields):
    payload = {
        "table_name": table_name,
        "geometry_type": geometry_type,
        "srid": 4326,
        "fields": fields
    }
    response = client.post("/spatial-tables/", json=payload)
    assert response.status_code == expected_status
    if expected_status == 201:
        assert "created with geometry type" in response.json()["message"]
    elif expected_status == 422:
        assert "detail" in response.json() or "error" in response.json()

def test_list_spatial_tables():
    response = client.get("/spatial-tables/")
    assert response.status_code == 200
    assert "tables" in response.json()
    assert isinstance(response.json()["tables"], list)

def test_describe_and_delete_spatial_table():
    # Create a table with custom fields
    payload = {
        "table_name": "describe_me",
        "geometry_type": "POINT",
        "fields": [
            {"name": "label", "type": "VARCHAR(100)", "nullable": False},
            {"name": "created_at", "type": "DATE", "nullable": True}
        ]
    }
    response = client.post("/spatial-tables/", json=payload)
    assert response.status_code == 201
    # Describe
    desc = client.get("/spatial-tables/describe_me")
    assert desc.status_code == 200
    desc_json = desc.json()
    assert desc_json["table"] == "describe_me"
    columns = [col["column_name"] for col in desc_json["columns"]]
    assert "label" in columns
    assert "created_at" in columns
    assert "geometry" in columns
    # Delete
    delete = client.delete("/spatial-tables/describe_me")
    assert delete.status_code == 200
    assert "deleted" in delete.json()["message"]
    # Table should not exist anymore
    desc2 = client.get("/spatial-tables/describe_me")
    assert desc2.status_code == 404
