from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import whatsapp, leads, telegram
from app.db.database import engine
from app.db.base import Base

app = FastAPI(title="Study Visa Genie API")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handling
@app.middleware("http")
async def global_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {exc}"},
        )

# Startup: Create Tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create tables
        # Import all models here to register them with metadata
        from app.models.student import Student
        from app.models.application import VisaApplication
        from app.models.chat_log import ChatLog
        from app.models.appointment import Appointment
        from app.models.document import Document
        from app.models.admin import AdminUser
        
        await conn.run_sync(Base.metadata.create_all)

# Include Routers
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["Telegram"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
from app.api import analytics
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def home():
    return {"message": "Study Visa Genie API is Live"}
