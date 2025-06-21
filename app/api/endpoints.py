from fastapi import APIRouter, Request, Response
from app.db.supabase_client import get_supabase_client
import xml.etree.ElementTree as ET
import asyncio

router = APIRouter()

@router.post("/webhook/twilio")
async def webhook_twilio(request: Request):
    # Extract form data from Twilio POST request
    form_data = await request.form()
    from_number = form_data.get("From")
    body = form_data.get("Body")

    # Immediately prepare Twilio response
    twiml = ET.Element("Response")
    message = ET.SubElement(twiml, "Message")
    message.text = "Thanks! Your message has been received."
    response_xml = ET.tostring(twiml, encoding="unicode")

    # Return response to Twilio immediately
    # DO NOT wait for DB insert
    asyncio.create_task(insert_message_async(from_number, body))

    return Response(content=response_xml, media_type="application/xml")


async def insert_message_async(from_number, body):
    try:
        supabase = get_supabase_client()
        data = {
            "from_number": from_number,
            "body": body,
            "status": "pending"
        }
        supabase.table("sms_messages").insert(data).execute()
    except Exception as e:
        # Log or handle DB errors if needed (this won't affect Twilio response)
        print(f"Supabase insert failed: {e}")
