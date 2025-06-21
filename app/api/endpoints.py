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
        "status": "pending"
    }
    supabase.table("sms_messages").insert(data).execute()

    # Create TwiML response to acknowledge Twilio
    twiml = ET.Element("Response")
    message = ET.SubElement(twiml, "Message")
    message.text = "Thanks! Your message has been received."
    response_xml = ET.tostring(twiml, encoding="unicode")

    return Response(content=response_xml, media_type="application/xml")

@router.post("/process-messages")
async def process_messages():
    supabase = get_supabase_client()
    # Fetch pending messages
    response = supabase.table("sms_messages").select("*").eq("processing_status", "pending").execute()
    messages = response.data
    
    results = []
    for msg in messages:
        from_number = msg["from_number"]
        body = msg["body"].strip().lower()
        msg_id = msg["id"]
        
        if "list" in body:
            # Fetch all list items
            items_response = supabase.table("list_items").select("item").execute()
            items = [item["item"] for item in items_response.data]
            result = f"Reply to {from_number}: Your list: {', '.join(items) if items else 'empty'}."
            status = "success"
        
        elif body.startswith("add "):
            item = body[4:]  # Get item after 'add '
            supabase.table("list_items").insert({
                "item": item,
                "added_by": from_number
            }).execute()
            result = f"Reply to {from_number}: '{item}' added to your list."
            status = "success"
        
        elif body.startswith("remove "):
            item = body[7:]  # Get item after 'remove '
            supabase.table("list_items").delete().eq("item", item).execute()
            result = f"Reply to {from_number}: '{item}' removed from your list."
            status = "success"
        
        else:
            result = f"Reply to {from_number}: Unrecognized command."
            status = "error"
        
        print(f"Updating message ID {msg_id} with status '{status}'")
        supabase.table("sms_messages").update({"processing_status": status}).eq("id", msg_id).execute()
        results.append(result)

    return {"processed": results}
    
@router.delete("/delete-message/{msg_id}")
async def delete_message(msg_id: int):
    supabase = get_supabase_client()
    response = supabase.table("sms_messages").delete().eq("id", msg_id).execute()
    return {"delete_response": response}

