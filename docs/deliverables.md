# Deliverable checklist

| ID | Deliverable | Files | State |
|---|---|---|---|
| D01 | Repository setup, README, ignore, branch model, env example | `.gitignore`, `README.md`, `CONTRIBUTING.md`, `.env.example` | Files ready; develop branch/commit unavailable because `.git` is read-only in this workspace |
| D02 | Requirements and wireframes | `docs/requirements.md`, `docs/wireframes.md` | Complete |
| D03 | ER diagram, MySQL scripts, migration | `docs/database.md`, `database/schema.sql`, `database/seed.sql`, `backend/alembic/` | Complete |
| US04 | Auth and role-aware navigation skeleton | `backend/app/security.py`, `backend/app/main.py`, `frontend/src/main.jsx` | Complete |
| D04 | Vehicle monitoring | vehicle CRUD, GPS WebSocket, maintenance endpoint and page | Implemented |
| D05 | Fuel consumption | `FuelLog`, fill-up API, efficiency API/chart | Implemented |
| D06 | Route planning | nearest-neighbor optimizer and page | Implemented |
| D07 | Driver management | profiles, expiry alerts and messaging | Implemented |
| D08 | Inventory | SKU details and low-stock alert | Implemented |
| D09 | Receiving and putaway | receiving records and bin assignment | Implemented |
| D10 | Picking and packing | validated pick/pack transitions | Implemented |
| D11 | Warehouse reporting | utilization suggestion and CSV endpoint | Implemented |
| D12 | Shipment tracking | tracking lookup and status history | Implemented |
| D13 | Delivery scheduling | driver/vehicle/shipment assignment | Implemented |
| D14 | Customer notifications | mocked SMS/email log | Implemented |
| D15 | Proof of delivery | shipment-linked canvas signature and attachment API | Implemented |
| D16 | Route and schedule management | route/schedule records and capacity availability | Implemented |
| D17 | Fare calculation | validated distance/zone/discount quote | Implemented |
| D18 | Ticket booking and payment | booking CRUD, mock payment, QR reference and cancellation | Implemented |
| D19 | Realtime transit | transit updates over authenticated WebSocket | Implemented |
| D20 | QA report | `backend/tests/test_api.py`, `docs/test-report.md`, QA page | Authored; execution blocked by missing runtimes |
| D21 | API docs and final README | `docs/api.md`, `README.md` | Complete |
| D22 | Demo and presentation | `docs/demo-script.md`, `docs/presentation.md` | Complete |
| D23 | Release metadata and tag | `CHANGELOG.md`, tag `v1.0.0` | Changelog ready; Git tag unavailable while `.git` is read-only |

Run commands and current verification limits are listed in `README.md` and `docs/test-report.md`.
