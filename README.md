# PostGIS REST API Backend + Mapping Website

[![CI](https://github.com/Bandit253/Orata_mapper/actions/workflows/ci.yml/badge.svg)](https://github.com/Bandit253/Orata_mapper/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/Bandit253/Orata_mapper/badge.svg?branch=main)](https://coveralls.io/github/Bandit253/Orata_mapper?branch=main)

A full-stack platform for managing and visualizing spatial and a-spatial data:
- **Backend:** FastAPI REST API with PostgreSQL/PostGIS (dynamic table support, robust CRUD, modular, tested)
- **Frontend:** Modern mapping website (Maplibre + React) consuming all backend endpoints

See `PLANNING.md` for architecture and `TASKS.md` for progress.

---

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js & npm/yarn (for frontend)

## Quick Start

### Backend
1. Clone and set up Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Start PostGIS DB: `docker compose up -d db`
4. Run Alembic migrations: `alembic upgrade head`
5. Start FastAPI app: `uvicorn app.main:app --reload`
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Frontend
1. Go to `frontend/` and run:
   ```sh
   npm install
   npm start
   ```
2. The mapping website will run at http://localhost:3000 (default)
3. All map features are powered by FastAPI endpoints (see API docs)

---

## Folder Structure
- `app/` - FastAPI backend
- `frontend/` - Mapping website (Maplibre + React)
- `alembic/` - DB migrations
- `tests/` - Backend tests
- `db-data/` - Local Postgres data

## Features
- Full spatial/a-spatial CRUD via API & UI
- Dynamic table support
- Interactive mapping & editing
- Robust validation & error handling
- CI/CD with tests & coverage

## Testing
- **Backend:** `pytest`
- **Frontend:** `npm test` (Jest/React Testing Library), `npx cypress open` (E2E)

## Security
- All secrets managed via `.env`/environment variables
- No credentials in code

---

For detailed architecture and task breakdown, see `PLANNING.md` and `TASKS.md`.
