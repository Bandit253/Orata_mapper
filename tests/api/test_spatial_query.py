"""
Unit tests for spatial query/filter endpoints (dynamic table version).
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

@pytest.fixture(scope="function")
def insert_features():
    features = [
        {"name": "PointA", "geometry": {"type": "Point", "coordinates": [100.0, 0.0]}},
        {"name": "PointB", "geometry": {"type": "Point", "coordinates": [101.0, 1.0]}},
        {"name": "LineA", "geometry": {"type": "LineString", "coordinates": [[100.0, 0.0], [101.0, 1.0]]}},
        {"name": "PolyA", "geometry": {"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 0.0]]]}}
    ]
    ids = []
    for feat in features:
        resp = client.post(f"/features/{TEST_TABLE}/", json=feat)
        assert resp.status_code == 201
        ids.append(resp.json()["id"])
    yield ids
    # Teardown: delete features
    for id in ids:
        client.delete(f"/features/{TEST_TABLE}/{id}")

def test_query_intersects(insert_features):
    geojson = {"type": "Polygon", "coordinates": [[[99.5, -0.5], [101.5, -0.5], [101.5, 1.5], [99.5, 1.5], [99.5, -0.5]]]}
    response = client.post(f"/features/{TEST_TABLE}/query/intersects", json={"geometry": geojson})
    assert response.status_code == 200
    assert any(f["name"] == "PointA" for f in response.json())
    assert any(f["name"] == "PolyA" for f in response.json())

def test_query_within(insert_features):
    geojson = {"type": "Polygon", "coordinates": [[[99.5, -0.5], [101.5, -0.5], [101.5, 1.5], [99.5, 1.5], [99.5, -0.5]]]}
    response = client.post(f"/features/{TEST_TABLE}/query/within", json={"geometry": geojson})
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_query_bbox(insert_features):
    bbox = [99.5, -0.5, 101.5, 1.5]
    response = client.post(f"/features/{TEST_TABLE}/query/bbox", json={"bbox": bbox})
    assert response.status_code == 200
    assert len(response.json()) >= 2

def test_query_distance(insert_features):
    geojson = {"type": "Point", "coordinates": [100.0, 0.0]}
    response = client.post(f"/features/{TEST_TABLE}/query/distance", json={"geometry": geojson, "distance": 200000})
    assert response.status_code == 200
    assert any(f["name"] == "PointB" for f in response.json())

def test_query_buffer(insert_features):
    geojson = {"type": "Point", "coordinates": [100.0, 0.0]}
    response = client.post(f"/features/{TEST_TABLE}/query/buffer", json={"geometry": geojson, "buffer": 200000})
    assert response.status_code == 200
    assert any(f["name"] == "PointB" for f in response.json())
