TASKS.md
📦 1. Project Initialization
- [ ] Initialize Git repository
- [x] Create project directory structure
- [x] Set up virtual environment
- [x] Initialize FastAPI app with main.py
- [x] Create requirements.txt and install:
    - [x] fastapi
    - [x] uvicorn[standard]
    - [x] sqlalchemy
    - [x] geoalchemy2
    - [x] pydantic
    - [x] shapely
    - [x] psycopg2-binary
    - [x] python-dotenv
    - [x] pytest
    - [x] httpx
- [ ] Create .env and config.py for environment variables

🧱 2. Database Setup
- [x] Install and configure PostgreSQL with PostGIS extension
- [x] Create Docker Compose setup for Postgres + PostGIS
- [x] Create Alembic setup for DB migrations
- [x] Define base DB connection in app/db/session.py
- [x] Set up initial schema migration
    - [x] Generate first migration script with Alembic
    - [x] Apply migration to database

🗺️ 3. Model & Schema Definitions
- [x] Define SQLAlchemy models in app/models/
    - [x] Base model for common fields
    - [x] Spatial model with geometry fields (supports Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon)

🧪 4. Testing
- [x] Write and pass Pytest unit tests for all spatial CRUD endpoints
- [x] Validate geometry serialization and error handling

---

🚩 Next Steps
- [ ] Implement a-spatial (non-geometry) CRUD endpoints
- [ ] Add endpoints for creation of spatial tables (Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon) with user-defined fields
- [ ] Add database logic to support dynamic spatial table creation with custom fields
- [ ] Add endpoints for listing, deleting, and describing spatial tables
- [ ] Write and pass tests for all spatial table management endpoints
- [ ] Add API security (authentication/authorization)
- [ ] Improve OpenAPI documentation (FastAPI docs)
- [ ] Add pagination, filtering, and search for features
- [ ] Write and pass tests for new endpoints
- [ ] Update README.md for new features and setup

- [x] Define Pydantic schemas in app/schemas/
    - [x] Base, Create, U
<truncated 797 bytes>
 Create API router in app/api/routes/
    - [ ] GET /features/
    - [ ] GET /features/{id}
    - [ ] POST /features/
    - [ ] PUT /features/{id}
    - [ ] DELETE /features/{id}
- [ ] Handle GeoJSON input/output for geometries
- [ ] Add pagination (limit, offset) and sorting support

🔐 6. Authentication & Authorization
- [ ] Set up OAuth2 password flow with JWT
- [ ] Add login route (POST /auth/token)
- [ ] Secure endpoints:
    - [ ] Read-only for public
    - [ ] Write access for authenticated users
    - [ ] Admin-level access for deletes

🧪 7. Testing
- [x] Configure Pytest
- [x] Write unit tests for:
    - [x] Models
    - [x] Schemas
    - [x] CRUD operations
    - [x] API routes (including spatial queries for Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon)
- [x] Use test database with rollback strategy

---
### Discovered During Work
- [x] [2025-04-19] Implemented secret management: all hardcoded credentials removed, secrets injected via env or GitHub Secrets. Added .env.example and updated README for onboarding and security best practices.
- [x] Ensure CRUD and API tests cover Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon.
- [x] Add negative tests for invalid geometry input for all types.
- [ ] Add tests and support for GeometryCollection (if needed).
- [x] [2025-04-18] Refactor all spatial CRUD and query endpoints to accept a `table_name` parameter, supporting dynamic multi-table operations. Ensure all new logic is robustly tested.
- [x] [2025-04-18] Add robust geometry validation to Pydantic schemas for all geometry types. All invalid geometries are now rejected with 422 errors.

📜 8. API Documentation
- [ ] Leverage FastAPI's auto-generated Swagger/OpenAPI docs
- [ ] Add examples and field descriptions in Pydantic models
- [ ] Customize title, description, and version

📦 9. Dockerization
- [ ] Create Dockerfile for FastAPI app
- [ ] Add multi-service docker-compose.yml:
    - [ ] FastAPI backend
    - [ ] PostgreSQL with PostGIS
- [ ] Configure volumes and ports
- [ ] Add .dockerignore

🚀 10. Deployment
- [ ] Add production-ready settings (e.g., gunicorn)
- [ ] Add docker-compose.prod.yml
- [ ] Deploy to:
    - [ ] Render / Railway / Fly.io / VPS
- [ ] Enable HTTPS (Let's Encrypt or platform-managed)
- [ ] Monitor uptime/logs (optional: Sentry, Grafana)

🗺️ 11. (Optional) Future Enhancements
- [ ] Add WebSocket layer for real-time updates
- [ ] Integrate with Leaflet/OpenLayers frontend
- [ ] Add caching (Redis) for heavy spatial queries
- [ ] Add user/role management UI
