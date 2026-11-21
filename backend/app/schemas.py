from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal

class Login(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=190)
    password: str = Field(min_length=8, max_length=100)

class RecordIn(BaseModel):
    module: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=180)
    status: str = Field(default="Active", min_length=2, max_length=40)
    reference: str = Field(default="", max_length=100)
    location: str = Field(default="", max_length=180)
    quantity: float = Field(default=0, ge=0)
    details: dict[str, Any] = Field(default_factory=dict)

class RecordOut(RecordIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

class FuelIn(BaseModel):
    vehicle_id: int = Field(gt=0)
    liters: float = Field(gt=0)
    odometer_km: float = Field(ge=0)
    cost: float = Field(default=0, ge=0)

class NotificationIn(BaseModel):
    recipient: str = Field(min_length=3, max_length=180)
    channel: str = Field(pattern="^(email|sms)$")
    message: str = Field(min_length=1, max_length=1000)

class AssignmentIn(BaseModel):
    driver: str = Field(min_length=2, max_length=120)
    vehicle: str = Field(min_length=2, max_length=80)
    time_slot: str = Field(min_length=2, max_length=80)
    route: str = Field(default="", max_length=180)
    shipment: str = Field(default="", max_length=100)

class PickAction(BaseModel):
    action: Literal["start_pick","confirm_pick","confirm_pack"]

class ProofCapture(BaseModel):
    shipment_reference: str = Field(min_length=3,max_length=100)
    signer: str = Field(min_length=2,max_length=120)
    signature_data_url: str = Field(min_length=40,max_length=2_000_000,pattern=r"^data:image/png;base64,")
