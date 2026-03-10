from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RecordBase(BaseModel):
    name: str
    student_id: str
    invoice_number: str
    group_name: Optional[str] = "丘陵课题组"
    payment_type: Optional[str] = "对公"
    other_info: Optional[str] = None

class RecordCreate(RecordBase):
    pass

class RecordUpdate(BaseModel):
    name: Optional[str] = None
    student_id: Optional[str] = None
    invoice_number: Optional[str] = None
    group_name: Optional[str] = None
    payment_type: Optional[str] = None
    other_info: Optional[str] = None

class RecordResponse(RecordBase):
    id: int
    invoice_image: str
    order_image: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
