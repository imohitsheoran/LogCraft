# LogiCraft build plan

## Folder structure

```text
backend/          FastAPI application, SQLAlchemy models, schemas, API, auth, simulator
frontend/         React + Vite + Tailwind role-aware operations console
database/         MySQL 8 schema and seed scripts
alembic/          Database migration environment and initial migration
docs/             Requirements, wireframes, database, API, QA, demo and traceability
tests/            API and end-to-end smoke tests
docker-compose.yml
```

## Build order

1. D01 repository conventions, environment example and contribution guide.
2. D02 requirements and screen wireframes.
3. D03 normalized MySQL schema, ER diagram, seed dataset and migration.
4. US04 auth skeleton, JWT role checks, API health/docs and role-aware frontend navigation.
5. D04-D19 in epic order. Build reusable CRUD/search/filter/pagination and validation foundations first; specialize tracking, fuel, routes, drivers, warehouse, shipment, fares, bookings and transit behavior on top.
6. D20 API and UI verification report, D21 API documentation, D22 demo/presentation, D23 changelog/version/tag.

Each module includes seeded records, REST endpoints, frontend operations, and tests. External email, SMS and payment services are simulated for a self-contained demo.
