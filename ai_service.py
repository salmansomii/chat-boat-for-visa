import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    model = None

async def get_visa_counselor_response(user_message: str, history: list = [], context: dict = None) -> str:
    if not model:
        return "System Error: AI service currently unavailable."

    # Construct context from history if needed
    
    system_prompt = """
    You are the AI assistant for **Dashboard Visa Business**, an expert Study Visa Consultancy based in **Pakistan**.
    Your name is 'VisaBot'.
    
    Your Context:
    - **Target Audience**: Pakistani Students (Matric, FSc, O/A Levels).
    - **Currency**: Convert costs to **PKR (Lakhs/Crores)** where helpful (Approx 1 USD = 280 PKR).
    - **Local Docs**: Mention FRC (Family Registration Certificate), Polio Card, and IBCC attestation.
    
    Your goal is to:
    1. EXCLUSIVELY discuss **Study Visas** for Canada, UK, USA, and Australia.
    2. Collect student details if missing (Name, Age, Target Country).
    3. Guide them to "Apply Now".
    
    If asked about other topics (cooking, sports, etc.), politely decline and steer back to Study Visas.
    Keep responses concise (max 3 sentences) suitable for WhatsApp/Telegram.
    """

    context_str = ""
    if context:
        name = context.get("name") or "Student"
        country = context.get("country") or "Unknown"
        status = context.get("status") or "New"
        context_str = f"\n    Current Student Context:\n    - Name: {name}\n    - Interested Info: {country}\n    - Application Status: {status}\n"

    prompt = f"{system_prompt}{context_str}\n\nUser: {user_message}\nVisaGenie:"

    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "I'm having a little trouble thinking right now. Please ask again in a moment."
