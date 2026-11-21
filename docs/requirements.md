# Requirements and assumptions

LogiCraft P12 provides a role-aware logistics console for vehicles, fuel, routes, drivers, inventory, receiving, picking, warehouse, shipments, deliveries, notifications, proof of delivery, schedules, fares, bookings and transit.

## Acceptance scope

- Four seeded roles authenticate using JWT. Fleet Manager can create/edit/delete; Dispatcher can read/filter and update status/details; QA Reviewer and Developer have read access. Developer has health and OpenAPI access.
- Every module has paginated search/filter CRUD endpoints, validation and seeded demonstration records.
- Vehicle GPS and transit arrivals stream over WebSockets. Route optimization and fare quote are deterministic demo services. Payment, SMS and email are mocked.
- MySQL 8 is the Docker database. Local development defaults to SQLite when `DATABASE_URL` is omitted.

## Assumptions

- “The source text was cut off” in US54 is interpreted as final documentation and demo readiness.
- A shared operational record table contains common searchable fields. Module extension values are stored one per row in `record_attributes`, keyed by `(record_id, attribute)`, and exposed in the API as a JSON object. This removes the unnormalized JSON blob from the records table while keeping the module form extensible.
- Demo GPS uses coordinates around Delhi NCR and is illustrative only. INR fare rules are sample values.
- Ticket QR values and delivery signatures are represented as record metadata in this first demo; external gateways and messaging providers are not contacted.
- Test accounts share `Demo@1234` and are for local demonstration only.
