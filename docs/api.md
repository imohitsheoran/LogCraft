# API reference

Interactive OpenAPI: `http://localhost:8000/docs`; schema: `http://localhost:8000/openapi.json`.

Authenticate with `POST /api/auth/login` and send `Authorization: Bearer <access_token>` on protected calls. Roles are Fleet Manager, Dispatcher, Developer and QA Reviewer.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness |
| POST | `/api/auth/login` | Issue access token |
| GET | `/api/auth/me` | Current identity and role |
| GET | `/api/modules` | Module index |
| GET/POST | `/api/{module}` | Search/list with `q`, `status`, `location`, `page`, `page_size`; create |
| GET/PUT/DELETE | `/api/{module}/{id}` | Detail, update, delete |
| GET | `/api/{module}/{id}/history` | Status event history |
| GET | `/api/fuel/efficiency` | Demo vehicle km/l view |
| GET/POST | `/api/fuel/logs` | View fuel entries / add a validated fill-up |
| POST | `/api/routes/optimize` | Nearest-neighbor stop order, distance and ETA estimate |
| GET | `/api/fares/quote?distance_km=10&zone=standard` | Quote fare |
| POST | `/api/notifications/send` | Record a simulated email/SMS delivery |
| GET | `/api/warehouse/export.csv` | Download warehouse report |
| GET | `/api/warehouse/suggestion` | Suggest least-utilized putaway bin |
| POST | `/api/bookings/{id}/pay` | Approve mock payment and return QR ticket reference |
| POST | `/api/bookings/{id}/cancel` | Cancel booking and record mock refund status |
| GET | `/api/drivers/alerts` | Find licenses expiring within 60 days |
| GET | `/api/vehicles/maintenance-alerts` | Find vehicles due for service |
| GET | `/api/inventory/low-stock` | List items at/below reorder point |
| GET | `/api/schedules/availability` | Show route departures and remaining capacity |
| POST | `/api/picking/{id}/workflow` | Apply start-pick, confirm-pick or confirm-pack transition |
| GET | `/api/shipments/track/{tracking_number}` | Look up a shipment and status history |
| POST | `/api/receiving/{id}/putaway?bin_code=BIN-A01` | Assign received stock to a bin |
| POST | `/api/deliveries/{id}/assign` | Assign driver, vehicle and time slot |
| PATCH | `/api/{module}/{id}/status?status=In%20Transit` | Dispatcher status-only update |
| POST | `/api/proof-of-delivery/capture` | Validate shipment reference and save recipient signature |
| POST | `/api/proof-of-delivery/upload` | Attach PNG, JPEG or PDF (5 MB max) to a proof record |
| GET | `/api/proof-of-delivery/{id}/attachment` | Download the attached proof file |
| WS | `/api/ws/live?token=<jwt>` | Authenticated GPS points every 2 seconds |
| WS | `/api/ws/transit?token=<jwt>` | Authenticated arrival/delay updates every 3 seconds |

The CRUD schema requires a name and validates nonnegative quantity. Create/delete/full record edits are Fleet Manager-only. Fleet Managers and Dispatchers may use the status-only PATCH endpoint. Reads are available to all authenticated roles. FastAPI returns standard validation errors and HTTP error details.
