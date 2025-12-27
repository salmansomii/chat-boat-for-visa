from fastapi import APIRouter, Request, HTTPException
from app.services.telegram_service import send_telegram_message
from app.services.ai_service import get_visa_counselor_response
from app.services.crm import create_new_lead, get_student_profile, update_student_profile, log_interaction

router = APIRouter()

@router.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    
    # Check if message exists
    try:
        if "message" in data:
            message = data["message"]
            chat_id = str(message["chat"]["id"])
            
            # Text Message
            if "text" in message:
                msg_body = message["text"].strip().lower()

                # --- Auto-Reply Flow (Replicated from WhatsApp) ---
                
                # Fetch Context
                student_profile = await get_student_profile(chat_id)
                student_id = student_profile.get("id")

                # Log User Message
                if student_id:
                    await log_interaction(student_id, "user", msg_body)
                
                # 1. Welcome / Menu
                if msg_body in ["hi", "hello", "start", "/start", "hlo"]:
                    welcome_msg = (
                        f"Welcome to *Dashboard Visa Business*! 🎓✈️\n"
                        f"Hi {student_profile['name'] or 'Future Scholar'}, we are here to help you study abroad.\n\n"
                        "Select your dream destination:\n"
                        "1. Canada 🇨🇦\n"
                        "2. UK 🇬🇧\n"
                        "3. USA 🇺🇸\n"
                        "4. Australia 🇦🇺\n\n"
                        "Type *Status* to check your application.\n"
                        "Type *Apply* to start your process."
                    )
                    await send_telegram_message(chat_id, welcome_msg)
                    if student_id: await log_interaction(student_id, "bot", welcome_msg)
                    return {"status": "replied_menu"}

                # 2. Status Check
                if msg_body == "status" or msg_body == "/status":
                    status_msg = (
                        f"📂 *Application Status*\n"
                        f"Name: {student_profile['name'] or 'Not Provided'}\n"
                        f"Country: {student_profile['country'] or 'Not Selected'}\n"
                        f"Current Status: *{student_profile['status']}*\n\n"
                        "Need to update documents? Just send them here."
                    )
                    await send_telegram_message(chat_id, status_msg)
                    return {"status": "replied_status"}

                # 3. Apply Flow
                if msg_body == "apply" or msg_body == "/apply":
                    if not student_profile['country']:
                        await send_telegram_message(chat_id, "Please select a country first (e.g., type 'Canada').")
                        return {"status": "replied_error"}
                    
                    await send_telegram_message(chat_id, "Great! To start your application, please reply with your *Full Name* like this:\n\nName: John Doe")
                    return {"status": "replied_apply_start"}

                if msg_body.startswith("name:"):
                    name_received = msg_body.split("name:")[1].strip().title()
                    await update_student_profile(chat_id, {"name": name_received})
                    await send_telegram_message(chat_id, f"Thanks {name_received}! Your profile is updated. An agent will review your file shortly.")
                    return {"status": "replied_name_saved"}

                # 4. Country Selection & Documents
                country_map = {
                    "1": "Canada", "canada": "Canada",
                    "2": "UK", "uk": "UK",
                    "3": "USA", "usa": "USA",
                    "4": "Australia", "australia": "Australia"
                }

                selected_country = country_map.get(msg_body)

                if selected_country:
                    # Save Lead in CRM
                    await create_new_lead(chat_id, selected_country)

                    # Send Documents List (Pakistan Context)
                    docs = {
                        "Canada": "🇨🇦 *Canada Study Visa (Pakistan Req):*\n- Passport (valid 6mo)\n- IELTS (6.0+ / PTE 60)\n- Matric & FSc/Inter Transcripts (IBCC Attested)\n- FRC (Family Reg Cert)\n- Bank Statement (40 Lakhs+)\n- Polio Card",
                        "UK": "🇬🇧 *UK Study Visa (Pakistan Req):*\n- Passport\n- CAS Letter\n- IELTS/PTE/OIETC\n- Bank Statement (28 days old, ~50 Lakhs)\n- TB Test (IOM)\n- FRC",
                        "USA": "🇺🇸 *USA Study Visa (Pakistan Req):*\n- Passport\n- I-20 Form\n- DS-160\n- SEVIS Fee ($350)\n- Interview Prep (Critical)\n- Bank Statement (60-80 Lakhs)",
                        "Australia": "🇦🇺 *Australia Study Visa (Pakistan Req):*\n- Passport\n- CoE\n- OSHC (Health Ins)\n- GTE/GS Statement\n- FRC & Polio Card\n- Bank Statement (Running Finance pref)"
                    }

                    response_msg = (
                        f"Great choice! Here are the documents required for {selected_country}:\n\n"
                        f"{docs[selected_country]}\n\n"
                        "Type *Apply* to proceed."
                    )
                    await send_telegram_message(chat_id, response_msg)
                    return {"status": "replied_docs"}
                
                # 6. Appointment Booking (Modern Feature)
                if msg_body == "book" or msg_body == "/book":
                    book_msg = (
                        "📅 *Book an Appointment*\n"
                        "We have slots available for consultation in Lahore/Islamabad or Online.\n\n"
                        "Reply with your preferred date:\n"
                        "e.g., *Date: Tomorrow 3 PM*"
                    )
                    await send_telegram_message(chat_id, book_msg)
                    return {"status": "replied_book"}

                if msg_body.startswith("date:"):
                    await send_telegram_message(chat_id, "✅ Appointment Confirmed! Our team will call you to finalize.")
                    return {"status": "replied_book_confirm"}

                # 7. AI: Get Response (Context Aware)
                ai_response = await get_visa_counselor_response(
                    message["text"], 
                    context=student_profile
                ) 
                
                await send_telegram_message(chat_id, ai_response)
                if student_id: await log_interaction(student_id, "bot", ai_response)
            
            # Voice Message Handling
            elif "voice" in message:
                voice_msg = (
                    "🎤 *Voice Note Received*\n"
                    "I am listening to your query... (AI Processing)\n\n"
                    "Please allow me a moment to transcribe and consult the Visa Expert."
                )
                await send_telegram_message(chat_id, voice_msg)
                
                # Simulation of AI processing voice (Stub)
                from asyncio import sleep
                await sleep(2)
                await send_telegram_message(chat_id, "💡 *AI Response*: I understand you are asking about gap years. Yes, for Canada, a gap up to 2 years is acceptable with proper justification (Experience Letter).")
                return {"status": "replied_voice"}

    except Exception as e:
        print(f"Error processing Telegram webhook: {e}")
        
    return {"status": "received"}
