# OrataMap Frontend

This is the mapping website for OrataMap, built with React, Maplibre GL JS, and Material UI. It consumes all FastAPI backend endpoints for spatial and a-spatial data management.

## Features
- Interactive map with Maplibre GL JS
- Modular React components
- Ready for API integration (CRUD, queries, table management)
- Modern UI with Material UI
- TypeScript for safety and maintainability
- Testing setup with Jest and React Testing Library

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn

### Setup
```sh
cd frontend
npm install
npm start
```

- The app will run at http://localhost:3000
- Ensure the FastAPI backend is running at http://localhost:8000

## Project Structure
- `src/`
  - `components/` — Reusable React components (MapView, etc)
  - `pages/` — Top-level pages (App.tsx, etc)
  - `api/` — API client logic (to be implemented)
  - `tests/` — Frontend tests (to be implemented)

## Next Steps
- Implement API client for backend integration
- Add UI for feature/table CRUD
- Add authentication UI (when backend ready)
- Add tests for components and E2E flows

---
For backend setup and API details, see the main project README.
