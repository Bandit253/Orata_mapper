## Table Name Parameterization for Spatial CRUD and Queries

### Update (2025-04-18)

- [x] All spatial CRUD and query endpoints now accept a `table_name` parameter. Features can be created, read, updated, and deleted in any user-created spatial table.
- [x] API endpoints use `/features/{table_name}/...` style paths for all CRUD and queries.
- [x] CRUD/data access layer uses SQLAlchemy reflection to operate on the correct table at runtime.
- [x] Pydantic schemas robustly validate all geometry types (Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon).
- [x] All new logic is robustly tested with Pytest, including edge/failure cases and geometry validation.

_This change enables true multi-table spatial support and aligns with the extensible, modular architecture described above._

---

