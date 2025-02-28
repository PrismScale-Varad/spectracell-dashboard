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

def onboarding_email(provider_name: str, reset_link: str) -> tuple[str, str]:
    """Generates the onboarding email for regular users."""
    subject = "Welcome to SpectraCell – Set Up Your Account"
    body = f"""
    <p>Dear {provider_name},</p>

    <p>Welcome to SpectraCell! We’re excited to have you on board. Your provider account has been successfully created, 
    and you’re just one step away from accessing your personalized dashboard.</p>

    <p>To get started, please set up your password by clicking the link below:</p>

    <p><a href="{reset_link}"><strong>Create Your Password</strong></a></p>

    <p>This will grant you secure access to order tests, view patient results, and manage your account with ease.</p>

    <p>If you have any questions or need assistance, feel free to contact our support team at 
    <a href="mailto:support@spectracell.com">support@spectracell.com</a> or call us at <strong>+1 (713) 621-3101</strong>.</p>

    <p>Thank you for partnering with SpectraCell. We look forward to supporting you!</p>

    <p>Best regards,<br>The SpectraCell Team</p>
    """
    return subject, body


def onboarding_email_admin(email: str, reset_link: str) -> tuple[str, str]:
    """Generates the onboarding email for admins."""
    subject = "Set Up Your Admin Account"
    body = f"""
    <p>Hello,</p>

    <p>Your admin account has been successfully created. To secure your access, please set up your password using the link below:</p>

    <p><a href="{reset_link}"><strong>Set Your Password</strong></a></p>

    <p>This link will expire in <strong>24 hours</strong>.</p>

    <p>If you need any assistance, please contact our support team at <a href="mailto:support@spectracell.com">support@spectracell.com</a> or call us at <strong>+1 (713) 621-3101</strong>.</p>

    <p>Best regards,<br>The SpectraCell Team</p>
    """
    return subject, body


def reset_password_email(provider_name: str, reset_link: str) -> tuple[str, str]:
    """Generates the password reset email for regular users."""
    subject = "Reset Your SpectraCell Password"
    body = f"""
    <p>Dear {provider_name},</p>

    <p>We received a request to reset your password.</p>

    <p>To proceed, click the link below:</p>

    <p><a href="{reset_link}"><strong>Reset Your Password</strong></a></p>

    <p>If you did not request this change, you can safely ignore this email.</p>

    <p>For any concerns, reach out to our support team at <a href="mailto:support@spectracell.com">support@spectracell.com</a> or call <strong>+1 (713) 621-3101</strong>.</p>

    <p>Best regards,<br>The SpectraCell Team</p>
    """
    return subject, body


def reset_password_email_admin(email: str, reset_link: str) -> tuple[str, str]:
    """Generates the password reset email for admins."""
    subject = "Admin Password Reset Request"
    body = f"""
    <p>Hello,</p>

    <p>We received a request to reset your admin account password. Click the link below to set a new password:</p>

    <p><a href="{reset_link}"><strong>Reset Your Password</strong></a></p>

    <p>If you did not request this, you can safely ignore this email.</p>

    <p>For assistance, please contact our support team at <a href="mailto:support@spectracell.com">support@spectracell.com</a> or call <strong>+1 (713) 621-3101</strong>.</p>

    <p>Best regards,<br>The SpectraCell Team</p>
    """
    return subject, body