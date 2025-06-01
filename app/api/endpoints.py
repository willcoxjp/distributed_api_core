from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from app.db.supabase_client import get_supabase_client
import xml.etree.ElementTree as ET

router = APIRouter()

@router.post("/webhook/twilio")
async def webhook_twilio(request: Request):
    # Extract form data from Twilio POST request
    form_data = await request.form()
    from_number = form_data.get("From")
    body = form_data.get("Body")

    # Save message to Supabase
    supabase = get_supabase_client()
    data = {
        "from_number": from_number,
        "body": body,
        "processing_status": "pending"
    }
    supabase.table("sms_messages").insert(data).execute()

    # Create TwiML response to acknowledge Twilio
    twiml = ET.Element("Response")
    message = ET.SubElement(twiml, "Message")
    message.text = "Thanks! Your message has been received."
    response_xml = ET.tostring(twiml, encoding="unicode")

    return Response(content=response_xml, media_type="application/xml")
