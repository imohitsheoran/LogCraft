# Story traceability

| Story | Epic | Deliverable | API endpoint | Frontend page | Test |
|---|---|---|---|---|---|
| US01 | E01 | D01 | — | — | — |
| US02 | E01 | D03 | — | — | — |
| US03 | E01 | D02 | — | Wireframes | — |
| US04 | E01 | Auth skeleton | `/api/auth/*` | Login + role navigation | `test_health_and_auth`, `test_role_permissions` |
| US05-US07 | E02 | D04 | `/api/vehicles`, `/api/ws/live` | Vehicles | `test_module_seeded_and_search`, `test_create_validation_and_update_delete` |
| US08-US10 | E03 | D05 | `/api/fuel`, `/api/fuel/efficiency` | Fuel | same module API tests |
| US11-US13 | E04 | D06 | `/api/routes`, `/api/routes/optimize` | Routes | `test_special_endpoints` + module tests |
| US14-US16 | E05 | D07 | `/api/drivers` | Drivers | module tests |
| US17-US19 | E06 | D08 | `/api/inventory` | Inventory | module tests |
| US20-US22 | E07 | D09 | `/api/receiving` | Receiving | module tests |
| US23-US25 | E08 | D10 | `/api/picking` | Picking | module tests |
| US26-US28 | E09 | D11 | `/api/warehouse` | Warehouse | module tests |
| US29-US31 | E10 | D12 | `/api/shipments`, `/api/shipments/{id}/history` | Shipments | module tests |
| US32-US34 | E11 | D13 | `/api/deliveries` | Deliveries | module tests |
| US35-US37 | E12 | D14 | `/api/notifications` | Notifications | module tests |
| US38-US40 | E13 | D15 | `/api/proof-of-delivery` | Proof of delivery | module tests |
| US41-US43 | E14 | D16 | `/api/schedules` | Schedules | module tests |
| US44-US46 | E15 | D17 | `/api/fares`, `/api/fares/quote` | Fares | `test_special_endpoints` + module tests |
| US47-US49 | E16 | D18 | `/api/bookings` | Bookings | module tests |
| US50-US52 | E17 | D19 | `/api/transit`, `/api/ws/transit` | Transit | module tests |
| US53 | E18 | D20 | All module APIs | Test report | `backend/tests/test_api.py` |
| US54 | E18 | D21-D23 | OpenAPI | Demo script | `backend/tests/test_api.py` |
