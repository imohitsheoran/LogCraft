# Demo script

Start with `docker compose up --build` and open `http://localhost:5173`.

1. Sign in as `fleetmanager@logicraft.com` / `Demo@1234`. Show overview and live fleet map. Open Vehicles, search `record 01`, filter status, add and edit a vehicle, then show GPS updates.
2. Sign out and sign in as `dispatcher@logicraft.com` / `Demo@1234`. Show shipment/route/inventory visibility and update an operational status.
3. Sign out and use `developer@logicraft.com` / `Demo@1234`. Show read access, `/docs`, `/api/health`, route optimizer and fare quote.
4. Sign out and use `qa@logicraft.com` / `Demo@1234`. Show read-only module access and review `docs/test-report.md`.
5. Open Transit and observe arrivals/delays changing live. Mention integrations are mocked and demo data is seeded on first startup.
