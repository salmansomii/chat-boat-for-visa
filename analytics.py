from fastapi import APIRouter
from sqlalchemy import func, select
from app.db.database import AsyncSessionLocal
from app.models.application import VisaApplication
from app.models.student import Student
from app.models.chat_log import ChatLog

router = APIRouter()

@router.get("/stats")
async def get_stats():
    async with AsyncSessionLocal() as session:
        # Total Students/Leads
        total_leads = await session.scalar(select(func.count(Student.id)))
        
        # Visa Status Counts
        approved = await session.scalar(select(func.count(VisaApplication.id)).where(VisaApplication.status == "approved"))
        active = await session.scalar(select(func.count(VisaApplication.id)).where(VisaApplication.status != "rejected"))
        
        return {
            "total_leads": total_leads,
            "approved_visas": approved,
            "active_applications": active,
            "ai_engagement": "98.5%" # Mock for now or calculate based on chat logs
        }

@router.get("/stream")
async def get_chat_stream():
    async with AsyncSessionLocal() as session:
        # Fetch last 50 messages from all chats
        result = await session.execute(
            select(ChatLog)
            .order_by(ChatLog.created_at.desc())
            .limit(50)
        )
        logs = result.scalars().all()
        
        # Format for frontend
        return [
            {
                "id": log.id,
                "sender": log.sender,
                "text": log.message,
                "time": log.created_at.strftime("%I:%M %p"),
                "student_id": log.student_id
            }
            for log in reversed(logs) # Return chronological order
        ]
