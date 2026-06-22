import smtplib
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

from core.config import settings
from util.common import logger
from db.session import AsyncSessionLocal
from db.otp import OtpCodes, OtpPurpose
from core.security import pwd_context

def send_email(subject: str, recipient: str, body: str):
    """
    Sends an email using the SMTP settings configured in core/config.py.
    This is a synchronous function suitable for smtplib.
    """
    if not all([settings.SMTP_SERVER, settings.SMTP_PORT, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.EMAILS_FROM_EMAIL]):
        logger.warning("SMTP settings are not fully configured. Email not sent.")
        return

    message = MIMEMultipart()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
        logger.info(f"Email sent successfully to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")

async def send_verification_email(email: str, user_id: uuid.UUID = None):
    """
    Generates a 6-digit OTP, saves its hash to the database, and sends it via email.
    """
    # 1. Generate 6-digit OTP
    otp = "".join(secrets.choice("0123456789") for _ in range(6))
    
    # 2. Save OTP hash to database
    try:
        async with AsyncSessionLocal() as db:
            otp_hash = pwd_context.hash(otp)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            
            otp_entry = OtpCodes(
                user_id=user_id,
                email=email,
                otp_hash=otp_hash,
                purpose=OtpPurpose.SIGNUP,
                expires_at=expires_at
            )
            db.add(otp_entry)
            await db.commit()
            logger.info(f"OTP entry created for {email} with purpose {OtpPurpose.SIGNUP}")
    except Exception as e:
        logger.error(f"Failed to save OTP to database for {email}: {str(e)}")
        # We might still want to try sending the email, or maybe not if we can't verify it later.
        # For now, let's proceed with sending the email but logging the error.

    # 3. Send Email
    subject = "Verify your account"
    body = f"Welcome! Thank you for signing up. Your 6-digit verification code is: {otp}. This code will expire in 5 minutes."
    send_email(subject, email, body)
