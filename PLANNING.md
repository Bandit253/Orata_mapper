# Project Architecture & Planning

## Overview
This project is now a full-stack geospatial platform with:
- **Backend:** FastAPI + PostgreSQL/PostGIS REST API for spatial & a-spatial data (dynamic table support, robust CRUD, modular, tested).
- **Frontend:** Modern mapping website (Maplibre-based) consuming all backend endpoints for interactive data visualization and editing.

## Goals
- Provide a robust, extensible geospatial API.
- Deliver a user-friendly, interactive mapping web app.
- Maintain modularity, testability, and clear documentation throughout.

## Tech Stack
- **Backend:** Python, FastAPI, SQLAlchemy, GeoAlchemy2, Pydantic, PostgreSQL/PostGIS
- **Frontend:** Maplibre GL JS, React (recommended), TypeScript (preferred), UI library (e.g., MUI/Chakra), Axios/fetch for API calls
- **Testing:** Pytest (backend), Jest/React Testing Library (frontend), Cypress (E2E)
- **DevOps:** Docker, Docker Compose, GitHub Actions CI

## Folder Structure
- `app/` - FastAPI backend (models, schemas, api, db, crud, utils)
- `frontend/` - Mapping website (React + Maplibre, components, pages, api, tests)
- `alembic/` - DB migrations
- `tests/` - Backend tests
- `db-data/` - Local Postgres data

## Integration
- Frontend fetches spatial/a-spatial data from FastAPI endpoints (CRUD, queries, table management)
- All API features exposed in UI: table/feature creation, editing, deletion, querying, etc.

## Security & Extensibility
- API authentication (planned)
- Modular code for easy extension (new geometry types, UI features, etc.)

---

## Next Steps
- See TASKS.md for detailed breakdown.
- All new features must be robustly tested and documented.
