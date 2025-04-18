# PostGIS REST API Backend

[![CI](https://github.com/Bandit253/Orata_mapper/actions/workflows/ci.yml/badge.svg)](https://github.com/Bandit253/Orata_mapper/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/Bandit253/Orata_mapper/badge.svg?branch=main)](https://coveralls.io/github/Bandit253/Orata_mapper?branch=main)

A FastAPI-based RESTful backend for managing spatial and a-spatial data with PostgreSQL/PostGIS. Supports full CRUD for all geometry types, geospatial queries, and robust authentication.

See `PLANNING.md` for architecture and `TASKS.md` for progress.

---

## Prerequisites
- Docker & Docker Compose
- Python 3.10+

## Quick Start

### 1. Clone and set up virtual environment
```sh
python -m venv .env313
.\.env313\Scripts\activate  # Windows
# or
source .env313/bin/activate  # Linux/Mac
```

### 2. Install dependencies
```sh
pip install -r requirements.txt
```

### 3. Start PostgreSQL/PostGIS with Docker Compose
```sh
docker compose up -d db
```
- Data will persist in the local `db-data` folder.

### 4. Run Alembic migrations
```sh
alembic upgrade head
```

### 5. Start FastAPI app
```sh
uvicorn app.main:app --reload
```

- The API will be available at http://localhost:8000
- Interactive docs: http://localhost:8000/docs

---

## Spatial API Usage

### Dynamic Table Support
All spatial CRUD and query endpoints now require a `table_name` path parameter. This enables you to manage features in any user-created spatial table.

#### Example Endpoints
- Create feature: `POST /features/{table_name}/`
- List features: `GET /features/{table_name}/`
- Get feature: `GET /features/{table_name}/{feature_id}`
- Update feature: `PUT /features/{table_name}/{feature_id}`
- Delete feature: `DELETE /features/{table_name}/{feature_id}`
- Spatial queries: `POST /features/{table_name}/query/{operation}`

#### Example Request (Create Feature)
```json
POST /features/my_table/
{
  "name": "Test Feature",
  "description": "A point",
  "geometry": {
    "type": "Point",
    "coordinates": [100.0, 0.0]
  }
}
```

### Geometry Validation
- Point: Must have exactly two numeric coordinates.
- LineString: At least 2 points.
- Polygon: Each ring must have at least 4 points and be closed.
- MultiPoint: At least 1 point.
- MultiLineString: At least 1 LineString, each with at least 2 points.
- MultiPolygon: At least 1 Polygon, each ring closed and with at least 4 points.

Invalid geometries will be rejected with a 422 error.

### 6. Run Tests

To run tests locally:
```sh
pytest
```
- Tests are isolated and use a dedicated test database (see `.env.example`).
- CI runs all tests with coverage reporting and enforces clean DB state for every run.

#### Coverage
- Coverage is automatically reported in CI and visible via the badge above.

#### Secret Management
- All secrets (DB URLs, credentials, tokens) must be set via environment variables or `.env` (never committed).
- See `.env.example` for required variables.
- In CI, all secrets are injected via GitHub Actions Secrets.

---

## Folder Structure
- `app/` - Main FastAPI app (models, schemas, api, db, crud, utils)
- `alembic/` - Database migrations
- `tests/` - Pytest unit tests
- `db-data/` - Local persistent Postgres data

---

## Useful Commands
- Stop services: `docker compose down`
- View logs: `docker compose logs db`
- Remove volumes: `docker compose down -v`
