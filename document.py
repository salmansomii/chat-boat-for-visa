from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"))
    document_type = Column(String) # e.g., "passport", "transcript", "ielts"
    file_url = Column(String)
    status = Column(String, default="pending") # pending, verified, rejected
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("VisaApplication", back_populates="documents")
