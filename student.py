from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True) # Phone number
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    profile_data = Column(JSON, default={}) # AI extracted details: age, education, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("VisaApplication", back_populates="student")
    chat_logs = relationship("ChatLog", back_populates="student", order_by="ChatLog.created_at")
    appointments = relationship("Appointment", back_populates="student")
