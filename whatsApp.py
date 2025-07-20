# whatsApp.py
import os
from dotenv import load_dotenv
from twilio.rest import Client
from agents import function_tool

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(account_sid, auth_token)

@function_tool
def send_whatsApp_message(phone_number: str, message_text: str) -> str:
    """
    Send a WhatsApp message using Twilio API.
    """
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone_number}',
            body=message_text  # ✅ Use body for text messages
        )
        return f"Message sent to {phone_number}! SID: {message.sid}"
    except Exception as e:
        return f"Failed to send message: {str(e)}"
