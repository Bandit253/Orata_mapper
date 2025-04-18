"""
Pytest unit tests for spatial API endpoints (dynamic table version).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import text
from app.db.session import engine

client = TestClient(app)
TEST_TABLE = "test_features"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Create test table
    create_sql = f'''
    CREATE TABLE IF NOT EXISTS {TEST_TABLE} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        geometry geometry(GEOMETRY, 4326) NOT NULL
    )'''
    with engine.connect() as connection:
        connection.execute(text(create_sql))
        connection.commit()
    yield
    # Drop test table after tests
    with engine.connect() as connection:
        connection.execute(text(f"DROP TABLE IF EXISTS {TEST_TABLE} CASCADE"))
        connection.commit()

# Example geometries
POINT = {"type": "Point", "coordinates": [100.0, 0.0]}
LINESTRING = {"type": "LineString", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}
POLYGON = {"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}
MULTIPOINT = {"type": "MultiPoint", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}
MULTILINESTRING = {"type": "MultiLineString", "coordinates": [ [[100.0, 0.0], [101.0, 1.0]], [[102.0, 2.0], [103.0, 3.0]] ]}
MULTIPOLYGON = {"type": "MultiPolygon", "coordinates": [ [ [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]] ], [ [[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]] ] ]}

@pytest.fixture(params=[
    ("Test Point", POINT),
    ("Test LineString", LINESTRING),
    ("Test Polygon", POLYGON),
    ("Test MultiPoint", MULTIPOINT),
    ("Test MultiLineString", MULTILINESTRING),
    ("Test MultiPolygon", MULTIPOLYGON)
])
def spatial_payload(request):
    name, geometry = request.param
    return {
        "name": name,
        "description": f"A test {geometry['type']} feature",
        "geometry": geometry
    }

def test_create_feature(spatial_payload):
    resp = client.post(f"/features/{TEST_TABLE}/", json=spatial_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == spatial_payload["name"]
    assert data["geometry"]["type"] == spatial_payload["geometry"]["type"]

def test_read_features():
    resp = client.get(f"/features/{TEST_TABLE}/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_update_feature():
    resp = client.post(f"/features/{TEST_TABLE}/", json={"name": "UpdateTest", "description": "desc", "geometry": POINT})
    feature_id = resp.json()["id"]
    update = {"name": "UpdatedName"}
    resp = client.put(f"/features/{TEST_TABLE}/{feature_id}", json=update)
    assert resp.status_code == 200
    assert resp.json()["name"] == "UpdatedName"

def test_delete_feature():
    resp = client.post(f"/features/{TEST_TABLE}/", json={"name": "DeleteTest", "description": "desc", "geometry": POINT})
    feature_id = resp.json()["id"]
    resp = client.delete(f"/features/{TEST_TABLE}/{feature_id}")
    assert resp.status_code == 200
    # Ensure feature is deleted
    resp = client.get(f"/features/{TEST_TABLE}/")
    assert all(f["id"] != feature_id for f in resp.json())

def test_invalid_geometry():
    payload = {"name": "Bad Feature", "geometry": {"type": "InvalidType", "coordinates": []}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
    payload = {"name": "Bad LineString", "geometry": {"type": "LineString", "coordinates": [[100.0, 0.0]]}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
    payload = {"name": "Bad Polygon", "geometry": {"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0]]]}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
    payload = {"name": "Bad MultiPoint", "geometry": {"type": "MultiPoint", "coordinates": []}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
    payload = {"name": "Bad MultiLineString", "geometry": {"type": "MultiLineString", "coordinates": [[[100.0, 0.0]]]}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
    payload = {"name": "Bad MultiPolygon", "geometry": {"type": "MultiPolygon", "coordinates": [ [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0]]] ]}}
    resp = client.post(f"/features/{TEST_TABLE}/", json=payload)
    assert resp.status_code == 422
