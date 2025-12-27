from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

class ApplicationStatus(str, enum.Enum):
    NEW_LEAD = "new_lead"
    DOCS_PENDING = "docs_pending"
    DOCS_RECEIVED = "docs_received"
    APPLIED = "applied"
    APPROVED = "approved"
    REJECTED = "rejected"

class VisaApplication(Base):
    __tablename__ = "visa_applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    country = Column(String) # Canada, UK, USA
    status = Column(String, default=ApplicationStatus.NEW_LEAD)
    university = Column(String, nullable=True)
    course = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="applications")
    documents = relationship("Document", back_populates="application")
