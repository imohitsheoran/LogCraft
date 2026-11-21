# QA test report

## Execution status

Automated test cases are provided in `backend/tests/test_api.py`, including parametrized create, validation and search/filter cases for all 16 modules, role restrictions and module-specific API checks. They could not be executed in this authoring environment: Python 3.11, Node.js and Docker executables are not installed/available in PATH. `python` resolves only to the Windows Store app alias; `npm.cmd` reports that `node` is unavailable. No passing result or coverage percentage is claimed without execution.

Run the checks in a configured environment:

```bash
cd backend && python -m pytest --cov=app --cov-report=term-missing
cd frontend && npm install && npm run build
docker compose up --build
```

## US53 end-to-end cases

| Case | Role | Steps | Expected result | Status |
|---|---|---|---|---|
| E2E-01 | Fleet Manager | Sign in, search vehicle, add/edit/delete record | CRUD succeeds and status history is recorded | Authored; not run here |
| E2E-02 | Dispatcher | Sign in, filter shipments, update status | Read/filter/status update succeeds; create denied | Authored; not run here |
| E2E-03 | Developer | Open health and OpenAPI docs | Health is OK and API schema loads | Authored; not run here |
| E2E-04 | QA Reviewer | Search module records and attempt mutation | Read works; mutation returns 403 | Authored; not run here |
| E2E-05 | Fleet Manager | Observe vehicle WebSocket feed | GPS messages update every two seconds | Authored; not run here |
| E2E-06 | QA Reviewer | Observe transit WebSocket feed | Arrivals/delay messages update every three seconds | Authored; not run here |
| E2E-07 | Developer | Request route optimization and fare quote | Deterministic route and INR quote are returned | Authored; not run here |
| E2E-08 | Dispatcher | Start picking, confirm picked and pack | Only valid order transitions are accepted and recorded | Authored; not run here |
| E2E-09 | Fleet Manager | Capture a shipment signature and attach a file | Shipment is validated; proof, signature and attachment are linked | Authored; not run here |

The codebase targets the requested 70%+ coverage but coverage remains unmeasured until pytest runs in an environment with the listed dependencies installed.
