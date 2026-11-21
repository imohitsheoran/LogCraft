from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.collections import attribute_keyed_dict
import re

def flatten_details(value, prefix=""):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from flatten_details(child, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten_details(child, f"{prefix}[{index}]")
    elif prefix:
        yield prefix, value

def unflatten_details(values):
    result = {}
    for path, value in values.items():
        parts = [part for part in re.split(r"\[(\d+)\]|\.", path) if part is not None and part != ""]
        target = result
        for index, part in enumerate(parts):
            last = index == len(parts)-1
            next_is_index = not last and parts[index+1].isdigit()
            key = int(part) if part.isdigit() else part
            if isinstance(target,list):
                while len(target) <= key: target.append(None)
                if last:
                    target[key] = value
                else:
                    if target[key] is None: target[key] = [] if next_is_index else {}
                    target = target[key]
            else:
                if last:
                    target[key] = value
                else:
                    if key not in target: target[key] = [] if next_is_index else {}
                    target = target[key]
    return result
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(30), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Record(Base):
    __tablename__ = "records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    status: Mapped[str] = mapped_column(String(40), default="Active", index=True)
    reference: Mapped[str] = mapped_column(String(100), default="")
    location: Mapped[str] = mapped_column(String(180), default="")
    quantity: Mapped[float] = mapped_column(Float, default=0)
    detail_rows: Mapped[dict[str, "RecordAttribute"]] = relationship(
        back_populates="record", cascade="all, delete-orphan",
        collection_class=attribute_keyed_dict("attribute"), lazy="selectin"
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def details(self):
        return unflatten_details({key: row.value for key,row in self.detail_rows.items()})

    @details.setter
    def details(self, value):
        rows=self.detail_rows
        flattened=dict(flatten_details(value or {}))
        for key in list(rows):
            if key not in flattened:
                del rows[key]
        for key, item in flattened.items():
            if key in rows:
                rows[key].value=item
            else:
                rows[key]=RecordAttribute(attribute=key,value=item)

class RecordAttribute(Base):
    __tablename__ = "record_attributes"
    record_id: Mapped[int] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), primary_key=True)
    attribute: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[object] = mapped_column("attribute_value", JSON, nullable=True)
    record: Mapped[Record] = relationship(back_populates="detail_rows")

class StatusEvent(Base):
    __tablename__ = "status_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("records.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(40))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FuelLog(Base):
    __tablename__ = "fuel_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("records.id"), index=True)
    liters: Mapped[float] = mapped_column(Float)
    odometer_km: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float, default=0)
    filled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
