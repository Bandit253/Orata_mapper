# TASKS.md

📦 1. Project Initialization
- [x] Create project directory structure
- [x] Set up virtual environment
- [x] Initialize FastAPI app with main.py
- [x] Create requirements.txt and install dependencies
- [x] Set up GitHub Actions CI

🧱 2. Database Setup
- [x] Install and configure PostgreSQL with PostGIS
- [x] Create Docker Compose setup
- [x] Set up Alembic for migrations
- [x] Define DB connection/session

🗺️ 3. Model & Schema Definitions
- [x] SQLAlchemy models (spatial/a-spatial)
- [x] Pydantic schemas (geometry validation)

🧪 4. Backend Testing
- [x] Pytest unit tests for all spatial CRUD endpoints
- [x] Validate geometry serialization and error handling

---

🚩 Next Steps (Backend)
- [ ] Implement a-spatial CRUD endpoints
- [ ] Add endpoints for spatial table creation (with custom fields)
- [ ] Add endpoints for listing, deleting, describing spatial tables
- [ ] Add API security (auth)
- [ ] Improve OpenAPI docs
- [ ] Pagination, filtering, search
- [ ] Write and pass tests for new endpoints

🗺️ 5. Mapping Website (Frontend)
- [ ] Set up `frontend/` project (React + Maplibre)
- [ ] Configure frontend build/dev environment
- [ ] Implement reusable map component (Maplibre GL JS)
- [ ] API client for FastAPI endpoints (CRUD, queries, table mgmt)
- [ ] UI for spatial table/feature creation, editing, deletion
- [ ] UI for querying and visualizing features
- [ ] Authentication UI (once backend ready)
- [ ] Unit tests (Jest/React Testing Library)
- [ ] E2E tests (Cypress)
- [ ] Write frontend setup/docs in README.md

---
### Discovered During Work
- [ ] Add tests/support for GeometryCollection (if needed)
- [ ] Add WebSocket layer for real-time updates (future)
- [ ] Add caching (Redis) for heavy spatial queries (future)
- [ ] Ability to remove layers from map (frontend only, not DB)
- [ ] Add layers to map from a view of what is in the DB
- [ ] Remove layers from DB (delete spatial table)
- [ ] Change symbology (layer styling)
- [ ] Ability to query a feature in the map
- [ ] Add a toolbar for spatial functions (API and frontend)
- [ ] Identify attributes of a feature (feature info popup)
- [ ] Move the import function to the toolbar
- [ ] Add user/role management UI (future)
