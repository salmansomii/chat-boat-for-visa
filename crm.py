from sqlalchemy.future import select
from app.db.database import AsyncSessionLocal
from app.models.student import Student
from app.models.application import VisaApplication, ApplicationStatus

async def get_or_create_student(whatsapp_id: str, name: str = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Student).where(Student.whatsapp_id == whatsapp_id))
        student = result.scalar_one_or_none()
        
        if not student:
            student = Student(whatsapp_id=whatsapp_id, name=name)
            session.add(student)
            await session.commit()
            await session.refresh(student)
        
        return student

async def create_new_lead(whatsapp_id: str, country_interest: str):
    student = await get_or_create_student(whatsapp_id)
    
    async with AsyncSessionLocal() as session:
        # Check if already has application for this country
        # For simplicity, just create new one
        new_app = VisaApplication(
            student_id=student.id,
            country=country_interest,
            status=ApplicationStatus.NEW_LEAD
        )
        session.add(new_app)
        await session.commit()
        return new_app

async def get_student_profile(whatsapp_id: str):
    student = await get_or_create_student(whatsapp_id)
    async with AsyncSessionLocal() as session:
        # Get latest application status
        result = await session.execute(
            select(VisaApplication).where(VisaApplication.student_id == student.id).order_by(VisaApplication.created_at.desc())
        )
        application = result.scalars().first()
        
        return {
            "id": student.id,
            "name": student.name,
            "country": application.country if application else None,
            "status": application.status if application else "No Application",
            "profile_data": student.profile_data
        }

async def update_student_profile(whatsapp_id: str, data: dict):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Student).where(Student.whatsapp_id == whatsapp_id))
        student = result.scalar_one_or_none()
        
        if student:
            if "name" in data:
                student.name = data["name"]
            if "email" in data:
                student.email = data["email"]
            
            # Merge profile_data
            current_data = student.profile_data or {}
            current_data.update(data.get("profile_data", {}))
            student.profile_data = current_data
            
            await session.commit()
            return True
        return False

from app.models.chat_log import ChatLog

async def log_interaction(student_id: int, sender: str, message: str):
    async with AsyncSessionLocal() as session:
        log = ChatLog(student_id=student_id, sender=sender, message=message)
        session.add(log)
        await session.commit()
