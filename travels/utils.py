import jwt
from django.conf import settings
from datetime import datetime, timedelta
import requests
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_jwt(user_id, email, is_admin=False):
    """
    Generate JWT token for users or admins.
    """
    role = "admin" if is_admin else "user"
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "is_staff": is_admin,   # ✅ useful for IsAdminUser
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")



def send_telegram_alert(message: str):
    bot_token = "8351219435:AAELR5JoLULoRmJZ-wR_jd-8MvwusEdjH0g"
    chat_id = "6223521733"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Telegram alert sent successfully")
    except Exception as e:
        print("⚠️ Failed to send Telegram alert:", e)

def generate_ticket_pdf(booking):
    """Generate PDF ticket for the user."""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, height - 100, "🚐 Travel Ticket Receipt")

    p.setFont("Helvetica", 12)
    y = height - 160

    details = [
        ("Booking ID", booking.get("booking_id")),
        ("Passenger Name", booking.get("name")),
        ("Email", booking.get("email")),
        ("Phone", booking.get("phone")),
        ("From", booking.get("origin")),
        ("To", booking.get("destination")),
        ("Pickup Point", booking.get("pickup_point")),
        ("Seat Number", booking.get("seat_number")),
        ("Amount Paid", f"₦{booking.get('amount')}"),
        ("Transaction ID", booking.get("transaction_id")),
        ("Company Website", "https://www.asaptravrls.ng"),
        ("Company Email", "asaptravels.ng01@gmail.com"),
    ]

    for label, value in details:
        p.drawString(80, y, f"{label}: {value}")
        y -= 25

    p.line(80, y - 10, width - 80, y - 10)
    y -= 40
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(80, y, "Please show this ticket to the driver at boarding.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# === Email Ticket ===
def send_ticket_email(email, booking):
    """Send ticket PDF to user's email."""
    pdf_buffer = generate_ticket_pdf(booking)
    email_msg = EmailMessage(
        subject="Your Travel Ticket 🎟️",
        body=f"Hello {booking.get('name')},\n\nYour booking (#{booking.get('booking_id')}) is confirmed.\n\nSafe travels with us!",
        from_email="support@yourcompany.com",
        to=[email],
    )
    email_msg.attach("travel_ticket.pdf", pdf_buffer.read(), "application/pdf")
    email_msg.send()
