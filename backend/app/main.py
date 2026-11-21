import asyncio
import base64
import math
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Literal
from fastapi import FastAPI, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .db import Base, engine, get_db, SessionLocal
from .models import User, Record, StatusEvent, FuelLog
from .schemas import Login, RecordIn, FuelIn, NotificationIn, AssignmentIn, PickAction, ProofCapture
from .security import verify_password, make_token, current_user, allow, hash_password, verify_token

MODULES = ["vehicles", "fuel", "routes", "drivers", "inventory", "receiving", "picking", "warehouse", "shipments", "deliveries", "notifications", "proof-of-delivery", "schedules", "fares", "bookings", "transit"]
ROLES = ["Fleet Manager", "Dispatcher", "Developer", "QA Reviewer"]

def record_dict(row):
    return {"id":row.id,"module":row.module,"name":row.name,"status":row.status,"reference":row.reference,"location":row.location,"quantity":row.quantity,"details":row.details,"updated_at":row.updated_at.isoformat() if row.updated_at else None}

def seed(db):
    accounts = [("fleetmanager@logicraft.com", "Avery Morgan", "Fleet Manager"), ("dispatcher@logicraft.com", "Jordan Lee", "Dispatcher"), ("developer@logicraft.com", "Sam Patel", "Developer"), ("qa@logicraft.com", "Taylor Chen", "QA Reviewer")]
    for email, name, role in accounts:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(email=email, full_name=name, role=role, password_hash=hash_password("Demo@1234")))
    db.flush()
    if db.query(Record).count() == 0:
        for module in MODULES:
            for i in range(1, 11):
                detail = {"priority": "normal", "demo": True}
                if module == "drivers":
                    detail.update(phone=f"+91-98{10000000+i:08d}", license_expiry=(datetime.utcnow()+timedelta(days=30+i*12)).date().isoformat(), assigned_vehicle=f"LC-{100+i}")
                elif module == "vehicles":
                    detail.update(plate_number=f"DL-01-AB-{1000+i}",make=["Tata","Ashok Leyland","Mahindra"][i%3],maintenance_due=(datetime.utcnow()+timedelta(days=(i%5)*9-5)).date().isoformat())
                elif module == "inventory":
                    detail.update(sku=f"SKU-{2000+i}", reorder_level=25, low_stock=(i <= 3))
                elif module == "routes":
                    detail.update(stops=["North Hub", "Central Depot", "South Yard"][:2+i%2], vehicle=f"LC-{100+i}")
                elif module == "shipments":
                    detail.update(tracking_number=f"TRK-{5000+i}", destination=["North Hub", "Central Depot", "South Yard"][i%3])
                elif module == "warehouse":
                    detail.update(bin_code=f"BIN-{chr(65+i%5)}{i:02}", utilization_percent=15+i*8)
                elif module == "schedules":
                    detail.update(capacity=40, booked_seats=i*3, departure=f"{7+i%12:02}:30")
                elif module == "fares":
                    detail.update(zone="premium" if i%3 == 0 else "standard", base_rate=2.5 if i%3 == 0 else 1.5)
                elif module == "bookings":
                    detail.update(passenger=f"Demo passenger {i}", payment_status="pending", qr_ticket=None)
                elif module == "proof-of-delivery":
                    detail.update(shipment_reference=f"SHP-{7000+i}", signature_captured=False)
                elif module == "transit":
                    detail.update(route=f"R-{i}", arrival_minutes=3+i, delay_minutes=i%5)
                db.add(Record(module=module, name=f"{module.title()} record {i:02}", status=["Active", "In Transit", "Available", "Needs Review"][i % 4], reference=f"{module[:3].upper()}-{1000+i}", location=["North Hub", "Central Depot", "South Yard"][i % 3], quantity=100-i*3, details=detail))
        db.flush()
    # SQL seed imports keep generic names but are enriched with the same demo attributes.
    for module in MODULES:
        for index, record in enumerate(db.query(Record).filter_by(module=module).order_by(Record.id).all(), 1):
            detail = record.details or {}
            if module == "drivers": detail.setdefault("license_expiry", (datetime.utcnow()+timedelta(days=30+index*12)).date().isoformat())
            elif module == "vehicles": detail.setdefault("maintenance_due",(datetime.utcnow()+timedelta(days=(index%5)*9-5)).date().isoformat())
            elif module == "inventory": detail.update(sku=detail.get("sku",f"SKU-{2000+index}"),reorder_level=25,low_stock=index <= 3)
            elif module == "routes": detail.setdefault("stops",["North Hub","Central Depot","South Yard"][:2+index%2])
            elif module == "shipments": detail.setdefault("tracking_number",f"TRK-{5000+index}")
            elif module == "warehouse": detail.setdefault("utilization_percent",15+index*8)
            elif module == "schedules": detail.setdefault("capacity",40)
            elif module == "bookings": detail.setdefault("payment_status","pending")
            elif module == "proof-of-delivery": detail.setdefault("signature_captured",False)
            record.details = detail
    if db.query(FuelLog).count() == 0:
        vehicles = db.query(Record).filter_by(module="vehicles").order_by(Record.id).all()
        for index, vehicle in enumerate(vehicles, 1):
            base = 12000 + index * 137
            db.add(FuelLog(vehicle_id=vehicle.id, liters=40+index, odometer_km=base, cost=(40+index)*102, filled_at=datetime.utcnow()-timedelta(days=14)))
            db.add(FuelLog(vehicle_id=vehicle.id, liters=38+index, odometer_km=base+420+index*7, cost=(38+index)*104, filled_at=datetime.utcnow()-timedelta(days=2)))
    db.commit()

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    yield

app = FastAPI(title="LogiCraft Logistics API", version="1.0.0", description="Role-aware logistics and fleet operations API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "logicraft", "time": datetime.utcnow().isoformat()}

@app.post("/api/auth/login")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not user.active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return {"access_token": make_token(user), "token_type": "bearer", "user": {"id": user.id, "email": user.email, "name": user.full_name, "role": user.role}}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "name": user.full_name, "role": user.role}

@app.get("/api/modules")
def modules(user: User = Depends(current_user)):
    return [{"key": key, "label": key.replace("-", " ").title()} for key in MODULES]

@app.post("/api/fuel/logs", status_code=201)
def add_fuel_log(data: FuelIn, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager", "Dispatcher"))):
    vehicle = db.query(Record).filter_by(id=data.vehicle_id, module="vehicles").first()
    if not vehicle: raise HTTPException(404, "Vehicle not found")
    latest=db.query(FuelLog).filter_by(vehicle_id=vehicle.id).order_by(FuelLog.odometer_km.desc()).first()
    if latest and data.odometer_km < latest.odometer_km: raise HTTPException(422,"Odometer reading cannot decrease")
    row = FuelLog(**data.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return row

@app.get("/api/fuel/logs")
def list_fuel_logs(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(FuelLog).order_by(FuelLog.filled_at.desc()).limit(100).all()

@app.post("/api/notifications/send", status_code=201)
def send_notification(data: NotificationIn, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager", "Dispatcher"))):
    row = Record(module="notifications", name=f"{data.channel.upper()} to {data.recipient}", status="Sent (mock)", reference=f"MSG-{int(datetime.utcnow().timestamp())}", location=data.recipient, details={"channel":data.channel,"message":data.message,"provider":"local mock","delivered":True})
    db.add(row); db.commit(); db.refresh(row)
    return {"accepted":True,"provider":"local mock","notification":record_dict(row)}

@app.get("/api/warehouse/export.csv")
def warehouse_csv(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Record).filter_by(module="warehouse").order_by(Record.id).all()
    body = "id,name,reference,location,quantity,status\n" + "".join(f'"{r.id}","{r.name}","{r.reference}","{r.location}",{r.quantity},"{r.status}"\n' for r in rows)
    return Response(body, media_type="text/csv", headers={"Content-Disposition":"attachment; filename=warehouse-report.csv"})

@app.get("/api/warehouse/suggestion")
def putaway_suggestion(db: Session = Depends(get_db), user: User = Depends(current_user)):
    bins = db.query(Record).filter_by(module="warehouse").all()
    bin_record = min(bins,key=lambda row:(row.details or {}).get("utilization_percent",100)) if bins else None
    utilization = (bin_record.details or {}).get("utilization_percent",100) if bin_record else 0
    return {"bin": (bin_record.details or {}).get("bin_code",bin_record.reference) if bin_record else "BIN-A01", "reason":"Lowest recorded utilization", "available_capacity": 100-utilization if bin_record else 100}

@app.get("/api/inventory/low-stock")
def low_stock(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Record).filter_by(module="inventory").all()
    return [record_dict(row) for row in rows if row.quantity <= (row.details or {}).get("reorder_level",25) or (row.details or {}).get("low_stock",False)]

@app.get("/api/drivers/alerts")
def driver_alerts(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.query(Record).filter_by(module="drivers").all()
    return [record_dict(row) for row in rows if (row.details or {}).get("license_expiry", "9999") <= (datetime.utcnow()+timedelta(days=60)).date().isoformat()]

@app.get("/api/vehicles/maintenance-alerts")
def maintenance_alerts(db: Session = Depends(get_db), user: User = Depends(current_user)):
    deadline=(datetime.utcnow()+timedelta(days=30)).date().isoformat()
    rows=db.query(Record).filter_by(module="vehicles").all()
    return [record_dict(row) for row in rows if (row.details or {}).get("maintenance_due","9999") <= deadline or row.status=="Maintenance"]

@app.get("/api/schedules/availability")
def schedule_availability(db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows=db.query(Record).filter_by(module="schedules").all()
    return [{"id":row.id,"route":row.reference,"departure":(row.details or {}).get("departure"),"capacity":(row.details or {}).get("capacity",0),"booked":(row.details or {}).get("booked_seats",0),"available":max(0,(row.details or {}).get("capacity",0)-(row.details or {}).get("booked_seats",0))} for row in rows]

@app.post("/api/picking/{record_id}/workflow")
def picking_workflow(record_id: int, body: PickAction, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager","Dispatcher"))):
    row=db.query(Record).filter_by(id=record_id,module="picking").first()
    if not row: raise HTTPException(404,"Pick order not found")
    transitions={"start_pick":({"Active","Available","Pending"},"Picking"),"confirm_pick":({"Picking"},"Picked"),"confirm_pack":({"Picked"},"Packed")}
    allowed,next_status=transitions[body.action]
    if row.status not in allowed: raise HTTPException(409,f"Cannot {body.action} while order is {row.status}")
    previous=row.status;row.status=next_status
    row.details={**(row.details or {}),"last_action":body.action}
    db.add(StatusEvent(record_id=row.id,status=next_status,note=f"{body.action} from {previous}"));db.commit();db.refresh(row)
    return record_dict(row)

@app.post("/api/proof-of-delivery/upload")
async def upload_proof(record_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager"))):
    row=db.query(Record).filter_by(id=record_id,module="proof-of-delivery").first()
    if not row: raise HTTPException(404,"Proof record not found")
    if file.content_type not in {"image/png","image/jpeg","application/pdf"}: raise HTTPException(415,"Upload a PNG, JPEG or PDF file")
    content=await file.read(5*1024*1024+1)
    if len(content)>5*1024*1024: raise HTTPException(413,"File exceeds the 5 MB demo limit")
    row.details={**(row.details or {}),"attachment_name":file.filename,"attachment_content_type":file.content_type,"attachment_base64":base64.b64encode(content).decode("ascii")}
    db.commit()
    return {"record_id":row.id,"filename":file.filename,"size_bytes":len(content),"attached":True}

@app.get("/api/proof-of-delivery/{record_id}/attachment")
def download_proof_attachment(record_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row=db.query(Record).filter_by(id=record_id,module="proof-of-delivery").first()
    if not row: raise HTTPException(404,"Proof record not found")
    details=row.details or {}
    if not details.get("attachment_base64"): raise HTTPException(404,"No file is attached")
    content=base64.b64decode(details["attachment_base64"])
    name=str(details.get("attachment_name","proof-attachment")).replace('"',"").replace("\r","").replace("\n","")
    return Response(content,media_type=details.get("attachment_content_type","application/octet-stream"),headers={"Content-Disposition":f'attachment; filename="{name}"'})

@app.post("/api/proof-of-delivery/capture",status_code=201)
def capture_proof(body: ProofCapture, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager"))):
    shipment=next((row for row in db.query(Record).filter_by(module="shipments").all() if row.reference==body.shipment_reference or (row.details or {}).get("tracking_number")==body.shipment_reference),None)
    if not shipment: raise HTTPException(404,"Shipment reference or tracking number not found")
    row=Record(module="proof-of-delivery",name=f"POD for {shipment.reference}",reference=f"POD-{shipment.reference}",location=shipment.location,status="Delivered",quantity=1,details={"shipment_id":shipment.id,"shipment_reference":shipment.reference,"tracking_number":(shipment.details or {}).get("tracking_number"),"signer":body.signer,"signature_data_url":body.signature_data_url,"signature_captured":True,"captured_at":datetime.utcnow().isoformat()})
    db.add(row);db.flush();db.add(StatusEvent(record_id=row.id,status=row.status,note=f"Signed by {body.signer}"));db.commit();db.refresh(row)
    return record_dict(row)

@app.get("/api/shipments/track/{tracking_number}")
def track_shipment(tracking_number: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    for row in db.query(Record).filter_by(module="shipments").all():
        if (row.details or {}).get("tracking_number") == tracking_number:
            events = db.query(StatusEvent).filter_by(record_id=row.id).order_by(StatusEvent.created_at.desc()).all()
            return {"shipment":record_dict(row),"history":[{"status":event.status,"note":event.note,"created_at":event.created_at.isoformat()} for event in events]}
    raise HTTPException(404,"Tracking number not found")

@app.post("/api/bookings/{record_id}/pay")
def mock_payment(record_id: int, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager", "Dispatcher"))):
    row = db.query(Record).filter_by(id=record_id,module="bookings").first()
    if not row: raise HTTPException(404,"Booking not found")
    previous=row.status;row.status="Paid"; row.details={**(row.details or {}),"payment_provider":"mock","payment_status":"approved","qr_ticket":f"LC-TICKET-{row.reference}"};db.add(StatusEvent(record_id=row.id,status=row.status,note=f"Mock payment approved from {previous}"));db.commit()
    return {"payment":"approved","provider":"mock","qr_ticket":row.details["qr_ticket"],"booking_id":row.id}

@app.post("/api/bookings/{record_id}/cancel")
def cancel_booking(record_id: int, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager", "Dispatcher"))):
    row = db.query(Record).filter_by(id=record_id,module="bookings").first()
    if not row: raise HTTPException(404,"Booking not found")
    previous=row.status;row.status="Cancelled";db.add(StatusEvent(record_id=row.id,status=row.status,note=f"Booking cancelled from {previous}; mock refund pending"));db.commit()
    return {"booking_id":row.id,"status":row.status,"refund":"mock pending"}

@app.post("/api/receiving/{record_id}/putaway")
def putaway(record_id: int, bin_code: str = Query(min_length=2,max_length=30), db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager","Dispatcher"))):
    row = db.query(Record).filter_by(id=record_id,module="receiving").first()
    if not row: raise HTTPException(404,"Receipt not found")
    row.location=bin_code; row.status="Put away"; row.details={**(row.details or {}),"bin_code":bin_code}
    db.add(StatusEvent(record_id=row.id,status=row.status,note=f"Put away to {bin_code}")); db.commit(); db.refresh(row)
    return record_dict(row)

@app.post("/api/deliveries/{record_id}/assign")
def assign_delivery(record_id: int, assignment: AssignmentIn, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager","Dispatcher"))):
    row = db.query(Record).filter_by(id=record_id,module="deliveries").first()
    if not row: raise HTTPException(404,"Delivery not found")
    driver=db.query(Record).filter(Record.module=="drivers",or_(Record.name==assignment.driver,Record.reference==assignment.driver)).first()
    vehicle=db.query(Record).filter(Record.module=="vehicles",or_(Record.name==assignment.vehicle,Record.reference==assignment.vehicle)).first()
    if not driver: raise HTTPException(404,"Driver name or reference not found")
    if not vehicle: raise HTTPException(404,"Vehicle name or reference not found")
    shipment=None
    if assignment.shipment:
        shipment=db.query(Record).filter(Record.module=="shipments",or_(Record.name==assignment.shipment,Record.reference==assignment.shipment)).first()
        if not shipment: raise HTTPException(404,"Shipment name or reference not found")
    row.details={**(row.details or {}),**assignment.model_dump(),"driver_id":driver.id,"vehicle_id":vehicle.id,"shipment_id":shipment.id if shipment else None}
    row.status="Scheduled"; db.add(StatusEvent(record_id=row.id,status=row.status,note="Driver and vehicle assigned")); db.commit(); db.refresh(row)
    return record_dict(row)

@app.get("/api/{module}")
def list_records(module: str, q: str = "", status: str = "", location: str = "", page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(current_user)):
    if module not in MODULES: raise HTTPException(404, "Module not found")
    query = db.query(Record).filter(Record.module == module)
    if q: query = query.filter(or_(Record.name.ilike(f"%{q}%"), Record.reference.ilike(f"%{q}%"), Record.location.ilike(f"%{q}%")))
    if status: query = query.filter(Record.status == status)
    if location: query = query.filter(Record.location.ilike(f"%{location}%"))
    total = query.count()
    rows = query.order_by(Record.id).offset((page-1)*page_size).limit(page_size).all()
    return {"items": [record_dict(row) for row in rows], "total": total, "page": page, "page_size": page_size}

@app.post("/api/{module}", status_code=201)
def create_record(module: str, data: RecordIn, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager"))):
    if module not in MODULES: raise HTTPException(404, "Module not found")
    values = data.model_dump(); values["module"] = module
    row = Record(**values); db.add(row); db.commit(); db.refresh(row)
    db.add(StatusEvent(record_id=row.id, status=row.status, note="Record created")); db.commit()
    return record_dict(row)

@app.get("/api/fuel/efficiency")
def fuel_efficiency(db: Session = Depends(get_db), user: User = Depends(current_user)):
    output = []
    vehicles = db.query(Record).filter_by(module="vehicles").all()
    for vehicle in vehicles:
        logs = db.query(FuelLog).filter_by(vehicle_id=vehicle.id).order_by(FuelLog.odometer_km).all()
        km_per_liter = round((logs[-1].odometer_km-logs[-2].odometer_km)/logs[-1].liters, 1) if len(logs) >= 2 and logs[-1].liters else None
        output.append({"vehicle_id":vehicle.id,"vehicle":vehicle.name,"km_per_liter":km_per_liter,"latest_odometer_km":logs[-1].odometer_km if logs else None})
    return output

@app.get("/api/fares/quote")
def fare_quote(distance_km: float = Query(ge=0), zone: Literal["standard","premium"] = "standard", discount_percent: float = Query(0, ge=0, le=100), user: User = Depends(current_user)):
    base = 20 + distance_km * (2.5 if zone == "premium" else 1.5)
    return {"distance_km": distance_km, "zone": zone, "fare": round(base*(1-discount_percent/100), 2), "currency": "INR"}

@app.get("/api/{module}/{record_id}")
def get_record(module: str, record_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.query(Record).filter_by(module=module, id=record_id).first()
    if not row: raise HTTPException(404, "Record not found")
    return record_dict(row)

@app.put("/api/{module}/{record_id}")
def update_record(module: str, record_id: int, data: RecordIn, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager"))):
    row = db.query(Record).filter_by(module=module, id=record_id).first()
    if not row: raise HTTPException(404, "Record not found")
    previous = row.status
    for key, value in data.model_dump().items(): setattr(row, key, module if key == "module" else value)
    db.add(StatusEvent(record_id=row.id, status=row.status, note=f"Updated from {previous}")); db.commit(); db.refresh(row)
    return record_dict(row)

@app.patch("/api/{module}/{record_id}/status")
def update_status(module: str, record_id: int, status: str = Query(min_length=2,max_length=40), db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager","Dispatcher"))):
    row = db.query(Record).filter_by(module=module,id=record_id).first()
    if not row: raise HTTPException(404,"Record not found")
    old_status = row.status
    row.status = status
    db.add(StatusEvent(record_id=row.id,status=status,note=f"Status changed from {old_status}"))
    db.commit(); db.refresh(row)
    return record_dict(row)

@app.delete("/api/{module}/{record_id}", status_code=204)
def delete_record(module: str, record_id: int, db: Session = Depends(get_db), user: User = Depends(allow("Fleet Manager"))):
    row = db.query(Record).filter_by(module=module, id=record_id).first()
    if not row: raise HTTPException(404, "Record not found")
    db.delete(row); db.commit()

@app.get("/api/{module}/{record_id}/history")
def history(module: str, record_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(StatusEvent).filter_by(record_id=record_id).order_by(StatusEvent.created_at.desc()).all()

@app.post("/api/routes/optimize")
def optimize_route(stops: list[str], user: User = Depends(current_user)):
    if not stops: raise HTTPException(422,"At least one stop is required")
    known={"north hub":(28.7041,77.1025),"central depot":(28.6139,77.2090),"south yard":(28.5355,77.3910),"airport":(28.5562,77.1000),"east hub":(28.6280,77.2950),"west depot":(28.6510,77.1250)}
    def coord(name):
        value=known.get(name.lower())
        if value:return value
        seed=sum((index+1)*ord(char) for index,char in enumerate(name.lower()))
        return (28.45+(seed%500)/10000,77.0+((seed*7)%500)/10000)
    remaining=list(dict.fromkeys(stops));ordered=[remaining.pop(0)];distance=0.0
    while remaining:
        lat1,lon1=coord(ordered[-1])
        closest=min(remaining,key=lambda stop:math.dist((lat1,lon1),coord(stop)))
        lat2,lon2=coord(closest);distance+=math.dist((lat1,lon1),(lat2,lon2))*111
        ordered.append(closest);remaining.remove(closest)
    return {"stops":ordered,"distance_km":round(distance,1),"eta_minutes":round(distance/35*60+len(ordered)*5),"method":"nearest-neighbor demo heuristic"}

@app.websocket("/api/ws/live")
async def live_feed(ws: WebSocket):
    await ws.accept()
    try:
        verify_token(ws.query_params.get("token", ""))
    except HTTPException:
        await ws.close(code=4401)
        return
    try:
        tick = 0
        while True:
            tick += 1
            await ws.send_json({"type": "gps", "vehicle": f"LC-{100+tick%12}", "lat": round(28.45+(tick%10)*0.008, 5), "lng": round(77.02+(tick%9)*0.009, 5), "speed_kph": 30+tick%50, "status": "In Transit", "timestamp": datetime.utcnow().isoformat()})
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return

@app.websocket("/api/ws/transit")
async def transit_feed(ws: WebSocket):
    await ws.accept()
    try:
        verify_token(ws.query_params.get("token", ""))
    except HTTPException:
        await ws.close(code=4401)
        return
    tick = 0
    try:
        while True:
            tick += 1
            await ws.send_json({"route": f"R-{tick%8+1}", "stop": f"Stop {tick%10+1}", "arrival_minutes": 2+tick%18, "delay_minutes": tick%5, "status": "On time" if tick%5 == 0 else "Approaching"})
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        return
