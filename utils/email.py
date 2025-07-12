import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def generate_verification_code(length=6):
    """6 raqamli tasdiqlash kodi yaratish"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email: str, code: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Tasdiqlash kodi - Authentication"

        body = f"""
        Assalomu alaykum!

        Sizning tasdiqlash kodingiz: {code}

        Bu kod 10 daqiqa davomida amal qiladi.

        Agar bu so'rovni siz yuborgan bo'lmasangiz, bu xabarni e'tiborsiz qoldiring.

        Rahmat!
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Email yuborishda xatolik: {e}")
        return False