import requests
from app.core.config import settings

RESEND_API_KEY = settings.RESEND_API_KEY
RESEND_API_URL = "https://api.resend.com/emails"
SENDER_EMAIL = settings.SENDER_ADDRESS

def send_email(recipient: str, subject: str, body: str):
    if not RESEND_API_KEY or not SENDER_EMAIL:
        raise ValueError("Resend API key or sender email is not set")

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "from": SENDER_EMAIL,
        "to": [recipient],
        "subject": subject,
        "html": body,
    }

    response = requests.post(RESEND_API_URL, json=data, headers=headers)
    response.raise_for_status()

    return response.json()
