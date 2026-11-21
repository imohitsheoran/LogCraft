from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls
from pathlib import Path

OUT = Path(__file__).parent / "LogiCraft-Complete-Project-Deck.pptx"
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

NAVY = "0B1220"
PANEL = "111C2E"
PANEL2 = "16243A"
TEAL = "2DD4BF"
BLUE = "60A5FA"
GOLD = "FBBF24"
WHITE = "F5F7FB"
MUTED = "A7B3C7"
LINE = "29384F"
GREEN = "86EFAC"
RED = "FDA4AF"
FONT = "Aptos"

def rgb(value):
    return RGBColor.from_string(value)

def rect(slide, x, y, w, h, fill, radius=True, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = rgb(fill)
    shape.line.color.rgb = rgb(line or fill)
    if radius:
        try: shape.adjustments[0] = 0.12
        except Exception: pass
    return shape

def textbox(slide, x, y, w, h, text, size=16, color=WHITE, bold=False,
            align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.04,
            font=FONT, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(margin); tf.margin_right = Inches(margin)
    tf.margin_top = Inches(margin); tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]; p.alignment = align
    p.space_after = Pt(0)
    run = p.add_run(); run.text = text
    run.font.name = font; run.font.size = Pt(size); run.font.bold = bold
    run.font.italic = italic; run.font.color.rgb = rgb(color)
    return box

def add_bg(slide, accent=TEAL):
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = rgb(NAVY)
    # Fine top rule, plus a quiet lower-right glow block.
    rect(slide, 0, 0, 13.333, 0.055, accent, radius=False)

def footer(slide, number, section="LOGICRAFT  /  PROJECT P12"):
    textbox(slide, .55, 7.15, 8.8, .2, section, 8, MUTED, bold=True, valign=MSO_ANCHOR.MIDDLE)
    textbox(slide, 12.05, 7.12, .65, .22, f"{number:02d}", 9, MUTED, bold=True,
            align=PP_ALIGN.RIGHT, valign=MSO_ANCHOR.MIDDLE)

def new_slide(title, eyebrow="PROJECT OVERVIEW", accent=TEAL):
    slide = prs.slides.add_slide(BLANK); add_bg(slide, accent)
    textbox(slide, .62, .36, 9.8, .26, eyebrow.upper(), 9, accent, bold=True)
    textbox(slide, .6, .72, 12.0, .55, title, 27, WHITE, bold=True)
    rect(slide, .62, 1.4, .62, .045, accent, radius=False)
    footer(slide, len(prs.slides))
    return slide

def card(slide, x, y, w, h, title, body, accent=TEAL, body_size=13, title_size=15):
    rect(slide, x, y, w, h, PANEL, line=LINE)
    rect(slide, x, y, .055, h, accent, radius=False)
    textbox(slide, x+.18, y+.14, w-.34, .38, title, title_size, WHITE, bold=True)
    textbox(slide, x+.18, y+.57, w-.34, h-.68, body, body_size, MUTED)

def bullet_list(slide, x, y, w, h, items, size=15, color=MUTED, gap=5, dot=TEAL):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = Inches(.02); tf.margin_right = Inches(.03)
    tf.margin_top = Inches(.01); tf.margin_bottom = Inches(.01)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = "•  " + item; p.level = 0
        p.space_after = Pt(gap); p.font.name = FONT; p.font.size = Pt(size); p.font.color.rgb = rgb(color)
    return box

def label(slide, x, y, w, text, color=TEAL):
    rect(slide, x, y, w, .33, PANEL2, line=LINE)
    textbox(slide, x+.07, y+.025, w-.14, .25, text, 9, color, bold=True,
            align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

def connector(slide, x1, y1, x2, y2, color=LINE, width=2):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    return c

def add_table(slide, x, y, w, h, headers, rows, widths=None, font_size=10):
    tbl = slide.shapes.add_table(len(rows)+1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h)).table
    if widths:
        for i, val in enumerate(widths): tbl.columns[i].width = Inches(val)
    for r in range(len(rows)+1):
        for c in range(len(headers)):
            cell = tbl.cell(r,c); cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(PANEL2 if r == 0 else (PANEL if r%2 else NAVY))
            cell.margin_left = Inches(.08); cell.margin_right = Inches(.06)
            cell.margin_top = Inches(.035); cell.margin_bottom = Inches(.025)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text = headers[c] if r == 0 else str(rows[r-1][c])
            for p in cell.text_frame.paragraphs:
                p.space_after = Pt(0)
                for run in p.runs:
                    run.font.name = FONT; run.font.size = Pt(font_size if r else font_size+0.5)
                    run.font.bold = r == 0; run.font.color.rgb = rgb(TEAL if r == 0 else WHITE)
    return tbl

# 01 — cover
s = prs.slides.add_slide(BLANK); add_bg(s, TEAL)
rect(s, 8.8, .45, 3.95, 6.35, PANEL, line=LINE)
for i, (name, c) in enumerate([("FLEET", TEAL), ("WAREHOUSE", BLUE), ("SHIPMENTS", GOLD), ("TRANSIT", GREEN)]):
    y = 1.2 + i*1.18
    rect(s, 9.3, y, 2.95, .72, PANEL2, line=LINE)
    rect(s, 9.3, y, .09, .72, c, radius=False)
    textbox(s, 9.58, y+.19, 2.3, .28, name, 12, WHITE, bold=True)
    if i < 3: connector(s, 10.76, y+.72, 10.76, y+1.18, LINE, 2)
textbox(s, .78, .9, 6.8, .3, "PROJECT P12  ·  RELEASE 1.0.0", 11, TEAL, bold=True)
textbox(s, .75, 1.62, 7.3, 1.3, "LogiCraft", 46, WHITE, bold=True)
textbox(s, .8, 2.86, 7.1, 1.0, "Connected logistics &\nfleet operations", 27, MUTED, bold=True)
rect(s, .8, 4.35, .72, .055, TEAL, radius=False)
textbox(s, .8, 4.68, 6.5, .9, "A role-aware control console for fleet, warehouse, shipment and transit operations.", 17, WHITE)
textbox(s, .8, 6.55, 6.5, .32, "COMPLETE PROJECT BRIEF  ·  NOVEMBER 2026", 9, MUTED, bold=True)
footer(s, len(prs.slides))

# 02
s=new_slide("One console for connected operations", "EXECUTIVE SUMMARY")
card(s,.65,1.75,3.85,2.0,"Unified operations","Sixteen operational pages share common search, status, location, pagination and record history.",TEAL)
card(s,4.72,1.75,3.85,2.0,"Actionable workflows","From receiving and putaway to dispatch, proof of delivery, fare quote and ticket lifecycle.",BLUE)
card(s,8.79,1.75,3.85,2.0,"Live visibility","Role-aware dashboards combine seeded Delhi NCR fleet locations with GPS and transit WebSocket feeds.",GOLD)
textbox(s,.75,4.35,11.8,.42,"The demo’s value is the end-to-end flow: operational records are connected across modules and roles.",19,WHITE,bold=True)
bullet_list(s,.82,5.05,11.5,1.2,["React + Vite console  ·  FastAPI / SQLAlchemy API  ·  MySQL 8 in Compose, SQLite for local demo","JWT authentication and four roles; simulated external payments, email and SMS keep the demo self-contained"],14)

# 03
s=new_slide("The operating problem LogiCraft addresses","WHY THIS PRODUCT")
card(s,.68,1.75,3.86,2.12,"Disconnected signals","Fleet status, warehouse activity, shipments and transit updates can live in separate tools.",BLUE)
card(s,4.74,1.75,3.86,2.12,"Manual handoffs","Dispatch and warehouse teams need clear transitions, assignments and auditable status history.",GOLD)
card(s,8.8,1.75,3.86,2.12,"Limited visibility","Managers need current location, capacity, stock and delivery evidence in one place.",TEAL)
textbox(s,.8,4.35,11.6,.38,"LogiCraft’s response",16,TEAL,bold=True)
bullet_list(s,.8,4.82,11.5,1.45,["Shared record model makes common work searchable across operational domains.","Purpose-built actions turn a list of records into validated business workflows.","Role controls make responsibilities visible while the live demo illustrates status changes."],15)

# 04
s=new_slide("Product scope: 16 operational modules","CAPABILITY MAP")
groups=[("FLEET & ROUTING",["Vehicles","Fuel","Routes","Drivers"],TEAL),("WAREHOUSE",["Inventory","Receiving","Picking","Warehouse"],BLUE),
        ("SHIPMENT EXECUTION",["Shipments","Deliveries","Notifications","Proof of Delivery"],GOLD),
        ("SCHEDULED MOBILITY",["Schedules","Fares","Bookings","Transit"],GREEN)]
for idx,(title,items,c) in enumerate(groups):
    x=.7+(idx%2)*6.05; y=1.72+(idx//2)*2.25
    rect(s,x,y,5.75,1.92,PANEL,line=LINE); textbox(s,x+.22,y+.16,5.25,.27,title,11,c,bold=True)
    for j,item in enumerate(items): label(s,x+.22+(j%2)*2.65,y+.65+(j//2)*.52,2.35,item,c)
textbox(s,.8,6.45,11.2,.35,"Every module includes seeded records plus shared list/detail conventions; specialist endpoints add domain workflows.",12,MUTED)

# 05
s=new_slide("People, permissions and accountability","ROLE MODEL",BLUE)
rows=[("Fleet Manager","Full record CRUD; can operate all management tools","Owns configuration and corrective actions"),
      ("Dispatcher","Read and filter; update status and dispatch details","Moves work through daily execution"),
      ("Developer","Read-only; OpenAPI and health visibility","Inspects integration surface and service health"),
      ("QA Reviewer","Read-only operational visibility","Reviews behavior and demo evidence")]
add_table(s,.7,1.76,11.95,3.7,["ROLE","ACCESS","TYPICAL RESPONSIBILITY"],rows,[2.1,4.8,5.05],12)
rect(s,.75,5.8,11.8,.75,PANEL,line=LINE)
textbox(s,1.0,6.01,11.2,.3,"All demo accounts use the shared password  Demo@1234  ·  credentials are for local demo only",14,GOLD,bold=True,align=PP_ALIGN.CENTER)

# 06
s=new_slide("Architecture: UI, API, data and live feeds","SYSTEM DESIGN",TEAL)
nodes=[(.68,2.15,2.2,1.15,"React + Vite","Role-aware console",TEAL),(3.45,2.15,2.25,1.15,"FastAPI","REST + WebSockets",BLUE),
       (6.3,2.15,2.2,1.15,"SQLAlchemy","Models + validation",GOLD),(9.15,1.65,3.35,1.0,"MySQL 8","Docker Compose demo",GREEN),
       (9.15,3.0,3.35,1.0,"SQLite","Quick local development",GREEN)]
for x,y,w,h,t,b,c in nodes:
    rect(s,x,y,w,h,PANEL,line=LINE); rect(s,x,y,.06,h,c,radius=False)
    textbox(s,x+.18,y+.18,w-.3,.35,t,16,WHITE,bold=True); textbox(s,x+.18,y+.58,w-.3,.28,b,10,MUTED)
connector(s,2.9,2.72,3.45,2.72,TEAL,2); connector(s,5.7,2.72,6.3,2.72,BLUE,2)
connector(s,8.5,2.5,9.15,2.12,GOLD,2); connector(s,8.5,2.86,9.15,3.45,GOLD,2)
rect(s,2.68,4.62,4.35,.85,PANEL2,line=LINE); textbox(s,2.9,4.88,3.9,.28,"JWT Bearer auth  ·  role checks",13,TEAL,bold=True,align=PP_ALIGN.CENTER)
rect(s,7.55,4.62,4.7,.85,PANEL2,line=LINE); textbox(s,7.77,4.88,4.25,.28,"Authenticated GPS + transit WebSockets",13,BLUE,bold=True,align=PP_ALIGN.CENTER)
textbox(s,.8,6.12,11.7,.35,"External gateways are intentionally mocked; APIs provide deterministic demo behavior without third-party credentials.",13,MUTED)

# 07
s=new_slide("Data model: common core, module attributes","DATABASE DESIGN",GOLD)
card(s,.72,1.8,3.75,1.8,"users","Email, full name, role, password hash and active flag. JWT identities are checked on protected calls.",TEAL,12)
card(s,4.78,1.8,3.75,1.8,"records","Shared module/name/status/reference/location/quantity fields with updated timestamp and indexes.",BLUE,12)
card(s,8.84,1.8,3.75,1.8,"record_attributes","One scalar value per (record_id, attribute), assembled into API details; nested lists reconstructed.",GOLD,12)
card(s,.72,4.0,3.75,1.6,"status_events","Record-linked status history and notes. Child history is removed with its record.",GREEN,12)
card(s,4.78,4.0,3.75,1.6,"fuel_logs","Vehicle-linked liters, odometer, cost and fill timestamp for efficiency reporting.",TEAL,12)
card(s,8.84,4.0,3.75,1.6,"Database targets","MySQL 8 / InnoDB + utf8mb4 for Compose; SQLite fallback for a quick standalone run.",BLUE,12)
textbox(s,.85,6.2,11.3,.3,"Initial Alembic migration: backend/alembic/versions/0001_initial.py  ·  schema and seed SQL: database/",11,MUTED)

# 08
s=new_slide("Shared records make every module consistent","RECORD CONTRACT")
fields=[("IDENTITY","id · module · name"),("STATE","status · updated_at"),("OPERATIONS","reference · location · quantity"),("EXTENSIONS","details JSON assembled from attributes")]
for i,(a,b) in enumerate(fields):
    x=.7+i*3.13; rect(s,x,2.0,2.85,1.28,PANEL,line=LINE); textbox(s,x+.18,2.2,2.5,.26,a,10,TEAL,bold=True); textbox(s,x+.18,2.62,2.5,.45,b,13,WHITE,bold=True)
connector(s,3.55,2.64,3.83,2.64,LINE,2); connector(s,6.68,2.64,6.96,2.64,LINE,2); connector(s,9.81,2.64,10.09,2.64,LINE,2)
bullet_list(s,.88,4.05,11.5,1.6,["Every module uses consistent create/read/update/delete patterns with validation.","Lists support q search, status and location filters, page number and page size.","Special attributes stay flexible without making core status and search fields opaque."],15)
label(s,1.1,6.25,2.35,"COMMON OPERATIONS",TEAL); label(s,4.95,6.25,2.75,"DOMAIN DETAILS",BLUE); label(s,9.05,6.25,2.35,"AUDIT HISTORY",GOLD)

# 09
s=new_slide("Fleet visibility: know where work is","FLEET & FUEL",TEAL)
card(s,.72,1.8,3.8,1.65,"Vehicle operations","Vehicle records, status and location feed the operational overview.",TEAL)
card(s,4.77,1.8,3.8,1.65,"Live position","Authenticated WebSocket emits simulated GPS points every two seconds.",BLUE)
card(s,8.82,1.8,3.8,1.65,"Maintenance alerts","Find vehicles approaching configured service intervals.",GOLD)
rect(s,.78,3.9,7.45,1.65,PANEL,line=LINE)
textbox(s,1.0,4.12,6.9,.26,"FUEL ECONOMY LOOP",11,TEAL,bold=True)
textbox(s,1.0,4.58,6.85,.55,"Log liters, odometer and cost → compare vehicle efficiency (km/l) → spot unusual usage.",17,WHITE,bold=True)
rect(s,8.55,3.9,3.8,1.65,PANEL,line=LINE)
textbox(s,8.78,4.12,3.3,.26,"GPS ASSUMPTION",11,GOLD,bold=True)
textbox(s,8.78,4.56,3.24,.62,"Coordinates are simulated around Delhi NCR; map points illustrate the workflow.",13,MUTED)

# 10
s=new_slide("Plan routes and manage drivers","ROUTE OPERATIONS",BLUE)
for i,(n,t,b,c) in enumerate([
    ("01","Stops","Route records hold the planned locations and status.",TEAL),
    ("02","Optimize","Nearest-neighbor heuristic returns stop order, distance and ETA estimate.",BLUE),
    ("03","Assign","Delivery assignment links driver, vehicle and time slot.",GOLD),
    ("04","Monitor","Driver expiry and vehicle maintenance alerts surface follow-up work.",GREEN)]):
    x=.75+i*3.13; rect(s,x,2.05,2.83,2.45,PANEL,line=LINE); textbox(s,x+.2,2.26,.6,.35,n,13,c,bold=True); textbox(s,x+.2,2.88,2.35,.35,t,18,WHITE,bold=True); textbox(s,x+.2,3.42,2.35,.78,b,13,MUTED)
    if i<3: connector(s,x+2.83,3.25,x+3.08,3.25,LINE,2)
rect(s,.78,5.2,11.78,.76,PANEL2,line=LINE)
textbox(s,1.02,5.42,11.2,.3,"Demo planning is deterministic and explainable; distance and ETA are estimates, not an external routing service.",13,GOLD,bold=True,align=PP_ALIGN.CENTER)

# 11
s=new_slide("Warehouse flow: stock in, stock out","WAREHOUSE OPERATIONS",BLUE)
steps=[("RECEIVING","Receive quantities and assign a bin through putaway."),("INVENTORY","Track SKUs, stock levels and reorder thresholds."),("PICKING","Enforce start → confirm pick → confirm pack transitions."),("WAREHOUSE","Suggest least-utilized bin and export a CSV report.")]
for i,(t,b) in enumerate(steps):
    x=.7+i*3.14; rect(s,x,2.03,2.82,2.15,PANEL,line=LINE); textbox(s,x+.18,2.24,2.45,.28,f"0{i+1}  /  {t}",11,BLUE,bold=True); textbox(s,x+.18,2.78,2.42,1.0,b,14,WHITE,bold=True)
    if i<3: connector(s,x+2.82,3.1,x+3.08,3.1,BLUE,2)
card(s,1.15,4.82,5.2,1.22,"Low-stock alert","List inventory items at or below the reorder point.",GOLD,12,14)
card(s,6.82,4.82,5.2,1.22,"Workflow control","Invalid pick/pack transitions are rejected and status changes are recorded.",TEAL,12,14)

# 12
s=new_slide("Shipment execution: dispatch to evidence","SHIPMENTS & DELIVERY",GOLD)
flow=[("SHIPMENT","Track by reference"),("DELIVERY","Assign driver + vehicle"),("NOTIFY","Log simulated email/SMS"),("PROOF","Signature + attachment")]
for i,(t,b) in enumerate(flow):
    x=.76+i*3.13; rect(s,x,2.0,2.75,1.43,PANEL,line=LINE); textbox(s,x+.18,2.22,2.3,.28,t,12,GOLD,bold=True); textbox(s,x+.18,2.68,2.3,.48,b,13,WHITE,bold=True)
    if i<3: connector(s,x+2.75,2.73,x+3.07,2.73,TEAL,2)
bullet_list(s,.9,4.15,11.7,1.55,["Shipment tracking returns current status and linked status history.","Delivery assignment stores the operational pairing and time slot.","Proof capture validates shipment reference and stores the signature; optional PNG/JPEG/PDF attachment max 5 MB.","Notifications create a delivery log only; no external SMS or email provider is contacted."],14)

# 13
s=new_slide("Scheduled mobility: capacity to transit","TRANSIT & SCHEDULES",GREEN)
card(s,.75,1.9,3.72,2.05,"Schedules","Departures are linked to routes and seats; availability returns remaining capacity.",GREEN)
card(s,4.82,1.9,3.72,2.05,"Fare quote","Distance, zone and discount inputs return deterministic sample INR pricing.",GOLD)
card(s,8.89,1.9,3.72,2.05,"Booking lifecycle","Mock payment returns QR ticket reference; cancellation records refund status.",BLUE)
rect(s,1.05,4.55,11.18,1.02,PANEL2,line=LINE)
textbox(s,1.33,4.82,10.6,.38,"TRANSIT WEBSOCKET  →  simulated arrival and delay updates every 3 seconds",15,GREEN,bold=True,align=PP_ALIGN.CENTER)
textbox(s,1.1,6.05,11,.35,"Ticket QR values, payments and refunds are demo metadata and statuses—not connections to real gateways.",12,MUTED,align=PP_ALIGN.CENTER)

# 14
s=new_slide("User experience: role-aware operations console","FRONTEND")
rect(s,.75,1.82,7.5,4.55,PANEL,line=LINE)
rect(s,.75,1.82,7.5,.5,PANEL2,line=LINE); textbox(s,1.02,1.95,3,.2,"LOGICRAFT  /  OPERATIONS",9,TEAL,bold=True)
rect(s,.98,2.56,1.42,3.5,NAVY,line=LINE)
for i,t in enumerate(["Overview","Vehicles","Inventory","Shipments","Transit"]):
    label(s,1.08,2.78+i*.57,1.2,t,TEAL if i==0 else MUTED)
rect(s,2.67,2.56,5.25,1.15,PANEL2,line=LINE); textbox(s,2.92,2.75,4.7,.25,"Operational overview",15,WHITE,bold=True); textbox(s,2.92,3.15,4.5,.28,"Fleet status · shipment backlog · live feed",10,MUTED)
for i,(n,c) in enumerate([("VEHICLES",TEAL),("SHIPMENTS",BLUE),("LOW STOCK",GOLD)]):
    x=2.67+i*1.77; rect(s,x,3.98,1.58,.82,PANEL2,line=LINE); textbox(s,x+.13,4.15,1.3,.2,n,8,c,bold=True); textbox(s,x+.13,4.45,1.2,.2,"Live",12,WHITE,bold=True)
rect(s,2.67,5.02,5.25,1.04,PANEL2,line=LINE); textbox(s,2.92,5.22,4.7,.23,"Recent operational activity",12,WHITE,bold=True); textbox(s,2.92,5.62,4.7,.2,"Status updates appear in record history",9,MUTED)
textbox(s,8.72,2.02,3.7,.4,"FRONTEND STACK",11,TEAL,bold=True)
bullet_list(s,8.72,2.48,3.8,2.0,["React 18 + Vite","Lucide icons and charts","Role-aware navigation and actions","Search, filters, pagination","Canvas signature capture"],13)
textbox(s,8.72,4.85,3.65,.4,"BUILD",11,BLUE,bold=True)
textbox(s,8.72,5.27,3.65,.7,"npm run build → Vite production bundle",14,WHITE,bold=True)

# 15
s=new_slide("API surface: shared CRUD plus specialized actions","REST & REALTIME API",TEAL)
rows=[("Identity","/api/auth/login · /api/auth/me","JWT issue and current user"),
      ("Module index","/api/modules","Supported pages and module metadata"),
      ("List + create","GET/POST /api/{module}","q, status, location, page, page_size"),
      ("Record actions","GET/PUT/DELETE /api/{module}/{id}","Detail, update, delete"),
      ("History + status",".../{id}/history · PATCH .../{id}/status","Audit and dispatcher status change"),
      ("Realtime","/api/ws/live · /api/ws/transit","JWT-authenticated WebSocket feeds")]
add_table(s,.75,1.75,11.8,4.3,["AREA","PATH PATTERN","BEHAVIOR"],rows,[2.0,5.2,4.6],11)
textbox(s,.9,6.3,11.6,.3,"OpenAPI schema: /openapi.json  ·  Interactive docs: /docs  ·  Health check: /api/health",12,TEAL,bold=True,align=PP_ALIGN.CENTER)

# 16
s=new_slide("Specialized endpoints cover real work","API REFERENCE  /  1 OF 2",BLUE)
rows=[("Fleet & fuel","/api/fuel/efficiency · /api/fuel/logs · /api/vehicles/maintenance-alerts","Efficiency, fill-ups and service alerts"),
      ("Routes & drivers","/api/routes/optimize · /api/drivers/alerts","Stop order / ETA estimate; 60-day license expiry"),
      ("Inventory","/api/inventory/low-stock","At/below reorder point"),
      ("Warehouse","/api/warehouse/suggestion · /api/warehouse/export.csv","Putaway suggestion and CSV export"),
      ("Receiving & picking","/api/receiving/{id}/putaway · /api/picking/{id}/workflow","Bin assignment and validated transitions"),
      ("Shipment & delivery","/api/shipments/track/{tracking_number} · /api/deliveries/{id}/assign","Tracking/history; driver/vehicle/time slot")]
add_table(s,.72,1.72,11.9,4.85,["DOMAIN","ENDPOINTS","PURPOSE"],rows,[2.0,6.2,3.7],9.4)

# 17
s=new_slide("Specialized endpoints cover real work","API REFERENCE  /  2 OF 2",GOLD)
rows=[("Notifications","POST /api/notifications/send","Record simulated SMS/email log"),
      ("Proof of delivery","POST /api/proof-of-delivery/capture · /upload","Shipment-validated signature and file"),
      ("Proof attachment","GET /api/proof-of-delivery/{id}/attachment","Download linked attachment"),
      ("Schedules","GET /api/schedules/availability","Departures and remaining capacity"),
      ("Fares","GET /api/fares/quote?distance_km=10&zone=standard","Sample INR fare quote"),
      ("Bookings","POST /api/bookings/{id}/pay · /cancel","Mock ticket payment and cancellation"),
      ("Realtime","WS /api/ws/live?token=JWT · /api/ws/transit?token=JWT","Authenticated feed; token query parameter")]
add_table(s,.72,1.72,11.9,4.95,["DOMAIN","ENDPOINTS","PURPOSE"],rows,[2.0,6.2,3.7],9.3)

# 18
s=new_slide("Example workflows connect the modules","END-TO-END STORIES",TEAL)
flows=[("DISPATCH","Optimize stops → assign driver/vehicle → update delivery status → follow shipment history",TEAL),
       ("WAREHOUSE","Receive stock → select putaway bin → pick → pack → export utilization report",BLUE),
       ("DELIVERY EVIDENCE","Validate shipment → capture recipient signature → attach proof file",GOLD),
       ("PASSENGER TRIP","Check capacity → quote fare → mock payment + QR → cancel / refund status",GREEN)]
for i,(t,b,c) in enumerate(flows):
    x=.82+(i%2)*6.05; y=1.85+(i//2)*2.15; card(s,x,y,5.55,1.7,t,b,c,13,13)
textbox(s,.95,6.25,11.4,.28,"Each transition is exposed through a domain action and reflected in the shared operational record/history.",12,MUTED)

# 19
s=new_slide("Security, validation and operational controls","IMPLEMENTATION DETAILS",GOLD)
card(s,.75,1.8,3.78,1.9,"Authentication","JWT access token; protected routes require Bearer auth. User identity and role are checked per request.",TEAL,12)
card(s,4.78,1.8,3.78,1.9,"Authorization","Fleet Manager: full CRUD. Dispatcher: reads + status changes. Developer/QA: read-only.",BLUE,12)
card(s,8.81,1.8,3.78,1.9,"Validation","Pydantic schemas, nonnegative quantity, valid workflow transitions, upload allowlist and 5 MB cap.",GOLD,12)
bullet_list(s,.95,4.3,11.4,1.4,["Status history captures operational changes and notes.","WebSocket endpoints authenticate the user token before streaming.","CORS and secrets are configurable; change the demo JWT key and DB passwords before exposure.","Demo credentials, illustrative coordinates and mocked external services are not production settings."],14)

# 20
s=new_slide("QA: what is verified and what is simulated","QUALITY & SCOPE",GREEN)
rect(s,.75,1.8,4.0,1.35,PANEL,line=LINE); textbox(s,1.0,2.0,3.5,.25,"BACKEND AUTOMATION",10,TEAL,bold=True); textbox(s,1.0,2.43,3.5,.45,"52 passed",25,WHITE,bold=True)
rect(s,4.96,1.8,3.55,1.35,PANEL,line=LINE); textbox(s,5.2,2.0,3.0,.25,"FRONTEND BUILD",10,BLUE,bold=True); textbox(s,5.2,2.43,3.0,.45,"Vite build passed",19,WHITE,bold=True)
rect(s,8.72,1.8,3.85,1.35,PANEL,line=LINE); textbox(s,8.96,2.0,3.2,.25,"WARNING",10,GOLD,bold=True); textbox(s,8.96,2.43,3.2,.45,"1 deprecation notice",17,WHITE,bold=True)
bullet_list(s,.92,3.72,11.4,1.75,["Backend suite covers health/auth, role restrictions, all 16 module CRUD/search/filter/validation paths and specialized APIs.","Reported run: `backend/.venv/Scripts/python.exe -m pytest -q` → 52 passed; one Starlette/AnyIO deprecation warning.","`frontend`: `npm run build` succeeded; Vite transformed 1,576 modules.","Demo-only / not externally integrated: GPS, transit feed, route heuristic, INR price rules, payments, SMS and email."],13)
textbox(s,.98,6.4,11.2,.24,"Source docs contain an older QA note; figures above reflect the later executed verification run.",10,MUTED,italic=True)

# 21
s=new_slide("Run locally or with Docker Compose","DEMO & OPERATIONS",BLUE)
card(s,.75,1.82,5.7,2.13,"Docker path","Requirement: Docker Desktop + Compose v2.\n\nProject root: docker compose up --build\nUI: localhost:5173   ·   API: localhost:8000\nStop: docker compose down",TEAL,13,15)
card(s,6.78,1.82,5.7,2.13,"Local path","Python 3.11+ and Node 20+.\n\nBackend: install backend/requirements.txt; run uvicorn app.main:app --reload.\nFrontend: npm install; npm run dev.\nWithout DATABASE_URL, SQLite is used.",BLUE,12,15)
rect(s,.82,4.48,11.65,1.2,PANEL2,line=LINE)
textbox(s,1.05,4.72,11.2,.28,"DEMO ACCOUNT",10,GOLD,bold=True,align=PP_ALIGN.CENTER)
textbox(s,1.05,5.06,11.2,.32,"fleetmanager@logicraft.com  /  Demo@1234     ·     dispatcher@logicraft.com     ·     developer@logicraft.com     ·     qa@logicraft.com",12,WHITE,bold=True,align=PP_ALIGN.CENTER)
textbox(s,.95,6.15,11.25,.42,"For the current local demo: http://127.0.0.1:5173  ·  docs at /docs  ·  health at /api/health",12,TEAL,bold=True,align=PP_ALIGN.CENTER)

# 22
s=new_slide("Suggested five-minute live demo","PRESENTATION RUN OF SHOW",TEAL)
demo=[("01 · MANAGER","Overview + live fleet map; search/filter vehicles; create/edit record; observe GPS feed."),
      ("02 · DISPATCHER","Inspect shipment/route/inventory; update an operational status."),
      ("03 · DEVELOPER","Open health + OpenAPI; show route optimizer and fare quote."),
      ("04 · QA REVIEWER","Demonstrate read-only experience and QA evidence."),
      ("05 · TRANSIT","Watch arrival and delay updates change live; explain simulated integrations.")]
for i,(t,b) in enumerate(demo):
    y=1.75+i*.91; rect(s,.8,y,11.7,.68,PANEL,line=LINE); textbox(s,1.02,y+.18,2.45,.22,t,10,TEAL,bold=True); textbox(s,3.53,y+.15,8.55,.32,b,12,WHITE)
textbox(s,.95,6.55,11.3,.2,"All demo accounts use Demo@1234; use each role to show permission differences.",10,MUTED,align=PP_ALIGN.CENTER)

# 23
s=new_slide("Requirements, traceability and delivery","PROJECT GOVERNANCE",BLUE)
card(s,.72,1.85,3.8,2.0,"Requirements","Acceptance scope is documented in docs/requirements.md; assumptions call out demo GPS, INR estimates and mocked gateways.",TEAL,12)
card(s,4.78,1.85,3.8,2.0,"Traceability","docs/traceability.md maps stories US01–US54 to epics, deliverables, endpoints, UI pages and tests.",BLUE,12)
card(s,8.84,1.85,3.8,2.0,"Release artifacts","README, API/database docs, demo script, changelog, SQL scripts, Alembic migration and test suite are included.",GOLD,12)
rect(s,.85,4.45,11.55,1.15,PANEL2,line=LINE)
textbox(s,1.12,4.69,11.0,.28,"D01–D23: repository setup → requirements + wireframes → data model → auth → 16 feature epics → QA → API/docs/demo/release",14,WHITE,bold=True,align=PP_ALIGN.CENTER)
textbox(s,1.02,6.05,11.1,.38,"Deliverable note: Git develop branch and v1.0.0 tag were not created because the workspace .git directory is read-only.",11,MUTED,italic=True,align=PP_ALIGN.CENTER)

# 24
s=new_slide("Current boundaries and next steps","ROADMAP",GOLD)
left=["Replace mock messaging/payment with sandbox providers.","Connect production fleet telemetry and transit data.","Replace nearest-neighbor heuristic with routing engine and traffic-aware ETA.","Add production secret management, monitoring and backup policy."]
right=["Add deployment environment configuration and HTTPS.","Expand end-to-end browser coverage and measure code coverage.","Add multi-tenant customer / organization isolation.","Review accessibility and operational analytics with real users."]
card(s,.78,1.83,5.65,3.32,"INTEGRATION ROADMAP","",TEAL)
bullet_list(s,1.02,2.55,5.1,2.4,left,13)
card(s,6.78,1.83,5.65,3.32,"PRODUCTION READINESS","",BLUE)
bullet_list(s,7.02,2.55,5.1,2.4,right,13)
textbox(s,1.05,5.82,11.0,.48,"Release 1.0.0 demonstrates the workflow foundation; production rollout requires real integrations and deployment hardening.",14,WHITE,bold=True,align=PP_ALIGN.CENTER)

# 25
s=prs.slides.add_slide(BLANK); add_bg(s,TEAL)
textbox(s,.85,1.15,4,.3,"LOGICRAFT  ·  PROJECT P12",11,TEAL,bold=True)
textbox(s,.8,2.1,10.5,.8,"One operating picture.",38,WHITE,bold=True)
textbox(s,.8,3.05,10.5,.8,"Fleet to final delivery.",38,WHITE,bold=True)
rect(s,.85,4.25,.75,.06,TEAL,radius=False)
textbox(s,.85,4.65,10.8,.45,"Connected logistics and fleet operations  ·  Release 1.0.0",18,MUTED)
textbox(s,.85,6.55,8.5,.26,"Demo app: 127.0.0.1:5173  ·  API: 127.0.0.1:8000/docs",11,TEAL,bold=True)
footer(s,len(prs.slides))

prs.core_properties.title = "LogiCraft — Complete Project Presentation"
prs.core_properties.subject = "Project P12: connected logistics and fleet operations"
prs.core_properties.author = "LogiCraft Project Team"
prs.core_properties.keywords = "Logistics, Fleet, Warehouse, Shipments, Transit, FastAPI, React"
prs.core_properties.comments = "Complete demo-ready project overview, workflows, architecture, API and QA reference."
prs.save(OUT)
print(f"Created {OUT} ({len(prs.slides)} slides, {OUT.stat().st_size:,} bytes)")
