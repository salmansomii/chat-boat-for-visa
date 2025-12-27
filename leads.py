from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import AsyncSessionLocal
from app.models.application import VisaApplication, ApplicationStatus
from app.models.student import Student

router = APIRouter()

# --- Pydantic Schemas ---
class StudentSchema(BaseModel):
    name: Optional[str]
    whatsapp_id: str
    email: Optional[str]
    profile_data: Optional[dict]

    class Config:
        from_attributes = True

class LeadResponse(BaseModel):
    id: int
    country: str
    status: str
    created_at: str
    student: StudentSchema

    class Config:
        from_attributes = True

class UpdateLeadRequest(BaseModel):
    status: str

# --- Endpoints ---

@router.get("/", response_model=List[LeadResponse])
async def get_leads():
    async with AsyncSessionLocal() as session:
        # Fetch applications with student data
        result = await session.execute(
            select(VisaApplication)
            .options(selectinload(VisaApplication.student))
            .order_by(VisaApplication.updated_at.desc())
        )
        leads = result.scalars().all()
        
        # Convert to response format
        response = []
        for lead in leads:
            response.append({
                "id": lead.id,
                "country": lead.country,
                "status": lead.status.value if hasattr(lead.status, 'value') else lead.status,
                "created_at": lead.created_at.isoformat() if lead.created_at else "",
                "student": {
                    "name": lead.student.name,
                    "whatsapp_id": lead.student.whatsapp_id,
                    "email": lead.student.email,
                    "profile_data": lead.student.profile_data
                }
            })
        return response

@router.patch("/{lead_id}")
async def update_lead_status(lead_id: int, update_data: UpdateLeadRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(VisaApplication).where(VisaApplication.id == lead_id))
        serialized_lead = result.scalar_one_or_none()
        
        if not serialized_lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Validate status enum if possible, or just accept string for flexibility
        # For now, trusting the input or mapping loosely
        valid_statuses = [s.value for s in ApplicationStatus]
        if update_data.status not in valid_statuses:
             raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

        serialized_lead.status = ApplicationStatus(update_data.status)
        await session.commit()
        await session.refresh(serialized_lead)
        
        return {"status": "success", "new_status": serialized_lead.status}

@router.get("/{student_id}/history")
async def get_lead_history(student_id: int):
    async with AsyncSessionLocal() as session:
        # Fetch chat logs
        from app.models.chat_log import ChatLog
        result = await session.execute(
            select(ChatLog)
            .where(ChatLog.student_id == student_id)
            .order_by(ChatLog.created_at.asc())
        )
        logs = result.scalars().all()
        
        return [
            {
                "sender": log.sender,
                "message": log.message,
                "timestamp": log.created_at.isoformat()
            }
            for log in logs
        ]
