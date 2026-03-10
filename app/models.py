from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    student_id = Column(String(50), nullable=False)
    invoice_number = Column(String(100), nullable=False, unique=True)
    group_name = Column(String(100), nullable=True, default="丘陵课题组")
    payment_type = Column(String(20), nullable=True, default="对公")
    other_info = Column(Text, nullable=True)
    invoice_image = Column(String(255), nullable=False)
    order_image = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
