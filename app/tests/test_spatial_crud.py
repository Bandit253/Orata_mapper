import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from app.main import app
from app.db.session import engine
from sqlalchemy import text

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
        geometry geometry(Point, 4326) NOT NULL
    )'''
    with engine.connect() as connection:
        connection.execute(text(create_sql))
        connection.commit()
    yield
    # Drop test table after tests
    with engine.connect() as connection:
        connection.execute(text(f"DROP TABLE IF EXISTS {TEST_TABLE} CASCADE"))
        connection.commit()

def feature_payload():
    return {
        "name": "Test Feature",
        "description": "A test feature",
        "geometry": {
            "type": "Point",
            "coordinates": [100.0, 0.0]
        }
    }

def test_create_feature():
    resp = client.post(f"/features/{TEST_TABLE}/", json=feature_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Feature"
    assert data["geometry"]["type"] == "Point"

def test_read_features():
    resp = client.get(f"/features/{TEST_TABLE}/")
    assert resp.status_code == 200
    features = resp.json()
    assert isinstance(features, list)
    assert any(f["name"] == "Test Feature" for f in features)

def test_update_feature():
    # Get the feature ID
    resp = client.get(f"/features/{TEST_TABLE}/")
    feature_id = resp.json()[0]["id"]
    update = {"name": "Updated Feature"}
    resp = client.put(f"/features/{TEST_TABLE}/{feature_id}", json=update)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Feature"

def test_delete_feature():
    # Get the feature ID
    resp = client.get(f"/features/{TEST_TABLE}/")
    feature_id = resp.json()[0]["id"]
    resp = client.delete(f"/features/{TEST_TABLE}/{feature_id}")
    assert resp.status_code == 200
    # Ensure feature is deleted
    resp = client.get(f"/features/{TEST_TABLE}/")
    assert all(f["id"] != feature_id for f in resp.json())

def test_invalid_table_name():
    resp = client.post(f"/features/invalid-table!@/", json=feature_payload())
    assert resp.status_code == 400

def test_invalid_geometry():
    bad_payload = feature_payload()
    bad_payload["geometry"] = {"type": "Point", "coordinates": []}
    resp = client.post(f"/features/{TEST_TABLE}/", json=bad_payload)
    assert resp.status_code == 422

def test_query_within():
    # Recreate a feature
    client.post(f"/features/{TEST_TABLE}/", json=feature_payload())
    geom = {"type": "Point", "coordinates": [100.0, 0.0]}
    resp = client.post(f"/features/{TEST_TABLE}/query/within", json={"geometry": geom})
    assert resp.status_code == 200
    assert any(f["name"] == "Test Feature" for f in resp.json())

def test_query_bbox():
    bbox = {"bbox": [99.0, -1.0, 101.0, 1.0]}
    resp = client.post(f"/features/{TEST_TABLE}/query/bbox", json=bbox)
    assert resp.status_code == 200
    assert any(f["name"] == "Test Feature" for f in resp.json())

def test_query_distance():
    geom = {"type": "Point", "coordinates": [100.0, 0.0]}
    resp = client.post(f"/features/{TEST_TABLE}/query/distance", json={"geometry": geom, "distance": 1000})
    assert resp.status_code == 200
    assert any(f["name"] == "Test Feature" for f in resp.json())

def test_query_intersects():
    geom = {"type": "Point", "coordinates": [100.0, 0.0]}
    resp = client.post(f"/features/{TEST_TABLE}/query/intersects", json={"geometry": geom})
    assert resp.status_code == 200
    assert any(f["name"] == "Test Feature" for f in resp.json())

def test_query_buffer():
    geom = {"type": "Point", "coordinates": [100.0, 0.0]}
    resp = client.post(f"/features/{TEST_TABLE}/query/buffer", json={"geometry": geom, "buffer": 0.1})
    assert resp.status_code == 200
    assert any(f["name"] == "Test Feature" for f in resp.json())
