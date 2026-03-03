from twilio.rest import Client
from app.config import settings


def send_otp_sms(phone_number: str, otp: str) -> bool:
    """
    Send OTP via SMS using Twilio.
    Returns True if sent successfully, False otherwise.
    """
    # In development, just print the OTP instead of sending SMS
    if settings.ENVIRONMENT == "development":
        print(f"[DEV MODE] OTP for {phone_number}: {otp}")
        return True

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your Movie App verification code is: {otp}. Valid for {settings.OTP_EXPIRE_MINUTES} minutes.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )
        return True
    except Exception as e:
        print(f"SMS send failed: {e}")
        return False