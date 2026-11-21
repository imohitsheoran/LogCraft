# LogiCraft — Comprehensive Logistics and Fleet Management Platform

Project P12, release 1.0.0. This demo combines fleet operations, warehouse workflows, shipment visibility, fares and transit updates in one role-aware console.

## Start with Docker

Requirements: Docker Desktop with Compose v2. From the project root:

```bash
docker compose up --build
```

On Windows, double-click `start.bat`; `stop.bat` stops the stack. Keep the start window open while demoing.

Open the UI at `http://localhost:5173`, API docs at `http://localhost:8000/docs`, and health at `http://localhost:8000/api/health`. Stop with Ctrl+C; run `docker compose down` to stop and `docker compose down -v` to reset the demo database volume.

Copy `.env.example` to `.env` to customize settings. Change the demo JWT key and database passwords before exposing the service beyond a local demo.

## Demo accounts

All passwords are `Demo@1234`.

| Role | Login |
|---|---|
| Fleet Manager | `fleetmanager@logicraft.com` |
| Dispatcher | `dispatcher@logicraft.com` |
| Developer | `developer@logicraft.com` |
| QA Reviewer | `qa@logicraft.com` |

Fleet Managers can create/edit/delete records, Dispatchers can read and change status only, and Developer/QA accounts are read-only. Developer has an in-app API docs and health page. API docs and health are also publicly available for the demo.

## Local development without Docker

Install Python 3.11+, Node 20+, and MySQL 8. The backend defaults to SQLite for a quick local demo, or point `DATABASE_URL` at MySQL. In separate terminals:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
# Windows PowerShell: npm.cmd install; npm.cmd run dev
```

For MySQL, the Docker backend applies the Alembic migration on startup; API startup then creates the demo users and 10 records per module. For a standalone MySQL 8 instance, run `mysql -u root -p < database/schema.sql`, then `mysql -u logicraft -plogicraft_demo logicraft < database/seed.sql`, and set `DATABASE_URL=mysql+pymysql://logicraft:logicraft_demo@localhost:3306/logicraft` before starting FastAPI.

## Modules and demo behaviors

Sixteen pages are available: vehicles, fuel, routes, drivers, inventory, receiving, picking, warehouse, shipments, deliveries, notifications, proof of delivery, schedules, fares, bookings and transit. Shared endpoints provide create/read/update/delete, pagination, search and filtering. Vehicle GPS and transit arrivals are simulated over authenticated WebSockets. Story-specific tools include fuel efficiency, nearest-neighbor stop optimization, driver expiry alerts and messaging, low-stock alerts, putaway workflow, pick/pack transitions, shipment lookup, delivery assignment, notification logs, canvas signature capture and optional file attachment, warehouse CSV, fare quoting and mock ticket payment/cancellation.

## Checks

```bash
cd backend
pip install -r requirements.txt
pytest
```

```bash
cd frontend
npm install
npm run build
```

## Project presentation

The complete, editable 25-slide overview is [LogiCraft-Complete-Project-Deck.pptx](LogiCraft-Complete-Project-Deck.pptx). The slide guide is [docs/presentation.md](docs/presentation.md), and `build_deck.py` recreates the deck.

## Project decisions

See [docs/PLAN.md](docs/PLAN.md), [docs/requirements.md](docs/requirements.md), [docs/database.md](docs/database.md), [docs/wireframes.md](docs/wireframes.md), [docs/traceability.md](docs/traceability.md), and [docs/deliverables.md](docs/deliverables.md). An initial migration is included in `backend/alembic/versions`. Common operational fields are relational; module-specific attributes use one atomic value per record/attribute key, with nested lists reconstructed for the API. See [docs/demo-script.md](docs/demo-script.md) and [docs/test-report.md](docs/test-report.md).
