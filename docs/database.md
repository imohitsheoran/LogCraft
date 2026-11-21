# Database design

MySQL 8 uses InnoDB, utf8mb4, indexed module/status/search and foreign keys. The shared `records` table holds common searchable operational fields. Module attributes live in `record_attributes`, one scalar per `(record_id, attribute)` key; the API assembles those rows as its `details` object. Users, status audit events and fuel logs are separate relational tables. A fuel log references its vehicle record. Status history and attributes are deleted with their parent record.

```mermaid
erDiagram
  USERS {
    int id PK
    varchar email UK
    varchar full_name
    varchar role
    varchar password_hash
    boolean active
  }
  RECORDS {
    int id PK
    varchar module
    varchar name
    varchar status
    varchar reference
    varchar location
    float quantity
    datetime updated_at
  }
  RECORD_ATTRIBUTES {
    int record_id PK,FK
    varchar attribute PK
    json attribute_value
  }
  STATUS_EVENTS {
    int id PK
    int record_id FK
    varchar status
    text note
    datetime created_at
  }
  FUEL_LOGS {
    int id PK
    int vehicle_id FK
    float liters
    float odometer_km
    float cost
    datetime filled_at
  }
  RECORDS ||--o{ STATUS_EVENTS : records
  RECORDS ||--o{ RECORD_ATTRIBUTES : attributes
  RECORDS ||--o{ FUEL_LOGS : vehicle
```

Apply with MySQL's init scripts via Compose, or run `mysql -u logicraft -p logicraft < database/schema.sql`. Alembic initial migration is at `backend/alembic/versions/0001_initial.py`.
