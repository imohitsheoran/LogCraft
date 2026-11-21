import os
os.environ["DATABASE_URL"] = "sqlite:///./test_logicraft.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app, MODULES

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def app_lifespan():
    with client:
        yield

def token(role="fleetmanager"):
    response=client.post("/api/auth/login",json={"email":f"{role}@logicraft.com","password":"Demo@1234"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_health_and_auth():
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me",headers={"Authorization":f"Bearer {token()}"}).status_code == 200

def test_role_permissions():
    assert client.post("/api/vehicles",json={"name":"Denied","module":"vehicles"},headers={"Authorization":f"Bearer {token('qa')}"}).status_code == 403
    dispatcher={"Authorization":f"Bearer {token('dispatcher')}"}
    first=client.get("/api/vehicles?page_size=1",headers=dispatcher).json()["items"][0]
    assert client.patch(f"/api/vehicles/{first['id']}/status?status=Maintenance",headers=dispatcher).status_code == 200
    assert client.put(f"/api/vehicles/{first['id']}",json={"name":"Not allowed","module":"vehicles"},headers=dispatcher).status_code == 403

def test_special_endpoints():
    h={"Authorization":f"Bearer {token()}"}
    assert client.get("/api/fares/quote?distance_km=10",headers=h).json()["fare"] == 35
    assert client.post("/api/routes/optimize",json=["Depot","North","East"],headers=h).status_code == 200
    assert client.get("/api/fuel/efficiency",headers=h).json()[0]["km_per_liter"] is not None
    assert len(client.get("/api/inventory/low-stock",headers=h).json()) >= 3
    assert client.get("/api/drivers/alerts",headers=h).status_code == 200
    assert len(client.get("/api/vehicles/maintenance-alerts",headers=h).json()) > 0
    assert len(client.get("/api/schedules/availability",headers=h).json()) >= 10
    delivery=client.get("/api/deliveries?page_size=1",headers=h).json()["items"][0]
    assigned=client.post(f"/api/deliveries/{delivery['id']}/assign",json={"driver":"Drivers record 01","vehicle":"Vehicles record 01","shipment":"Shipments record 01","time_slot":"09:00-11:00","route":"North Hub - Central Depot"},headers=h)
    assert assigned.status_code == 200 and assigned.json()["status"] == "Scheduled"
    assert client.get("/api/shipments/track/TRK-5001",headers=h).status_code == 200
    assert "text/csv" in client.get("/api/warehouse/export.csv",headers=h).headers["content-type"]
    pick=next(row for row in client.get("/api/picking?page_size=50",headers=h).json()["items"] if row["status"] in {"Active","Available","Pending"})
    picked=client.post(f"/api/picking/{pick['id']}/workflow",json={"action":"start_pick"},headers=h)
    assert picked.status_code == 200 and picked.json()["status"] == "Picking"
    assert client.post(f"/api/picking/{pick['id']}/workflow",json={"action":"confirm_pick"},headers=h).json()["status"] == "Picked"
    assert client.post(f"/api/picking/{pick['id']}/workflow",json={"action":"confirm_pack"},headers=h).json()["status"] == "Packed"
    signature="data:image/png;base64,"+"AA"*50
    assert client.post("/api/proof-of-delivery/capture",json={"shipment_reference":"missing","signer":"Demo","signature_data_url":signature},headers=h).status_code == 404
    proof=client.post("/api/proof-of-delivery/capture",json={"shipment_reference":"TRK-5001","signer":"QA Test","signature_data_url":signature},headers=h).json()
    upload=client.post("/api/proof-of-delivery/upload",data={"record_id":proof["id"]},files={"file":("pod.png",b"demo image","image/png")},headers=h)
    assert upload.status_code == 200 and upload.json()["attached"]
    assert client.get(f"/api/proof-of-delivery/{proof['id']}/attachment",headers=h).content == b"demo image"

def test_module_details_are_round_tripped_as_atomic_attributes():
    h={"Authorization":f"Bearer {token()}"}
    created=client.post("/api/routes",json={"module":"routes","name":"Nested details route","details":{"stops":["Depot A","Depot B"],"priority":"high"}},headers=h)
    assert created.status_code == 201
    assert created.json()["details"] == {"stops":["Depot A","Depot B"],"priority":"high"}
    with client.websocket_connect(f"/api/ws/transit?token={token()}") as socket:
        assert socket.receive_json()["route"].startswith("R-")

@pytest.mark.parametrize("module", MODULES)
def test_module_search_and_filter(module):
    h={"Authorization":f"Bearer {token()}"}
    page=client.get(f"/api/{module}?page=1&page_size=3",headers=h).json()
    assert page["total"] >= 10 and len(page["items"]) == 3
    found=client.get(f"/api/{module}?q=1002",headers=h).json()
    assert found["total"] == 1
    filtered=client.get(f"/api/{module}?status=In%20Transit&page_size=2",headers=h).json()
    assert filtered["total"] >= 1 and all(x["status"] == "In Transit" for x in filtered["items"])

@pytest.mark.parametrize("module", MODULES)
def test_module_create_and_update_delete(module):
    h={"Authorization":f"Bearer {token()}"}
    created=client.post(f"/api/{module}",json={"name":"QA test record","module":module,"quantity":12},headers=h)
    assert created.status_code == 201
    row=created.json(); assert client.get(f"/api/{module}/{row['id']}",headers=h).status_code == 200
    assert client.put(f"/api/{module}/{row['id']}",json={"name":"Updated record","module":module,"status":"In Transit"},headers=h).status_code == 200
    assert client.delete(f"/api/{module}/{row['id']}",headers=h).status_code == 204

@pytest.mark.parametrize("module", MODULES)
def test_module_validation_failure(module):
    h={"Authorization":f"Bearer {token()}"}
    response=client.post(f"/api/{module}",json={"name":"x","module":module,"quantity":-1},headers=h)
    assert response.status_code == 422
