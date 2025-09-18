import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings
from ..schemas import ContactCreate
from typing import Optional

def send_contact_notification(contact: ContactCreate) -> bool:
    """
    Send email notification when a new contact form is submitted
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = settings.SMTP_USERNAME  # Send to self
        msg['Subject'] = f"New Contact Form Submission from {contact.name}"
        
        # Create email body
        body = f"""
        New contact form submission received:
        
        Name: {contact.name}
        Email: {contact.email}
        Phone: {contact.phone or 'Not provided'}
        Company: {contact.company or 'Not provided'}
        
        Message:
        {contact.message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, settings.SMTP_USERNAME, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_contact_confirmation(contact: ContactCreate) -> bool:
    """
    Send confirmation email to the person who submitted the contact form
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = contact.email
        msg['Subject'] = "Thank you for contacting Arnetrice Smith"
        
        # Create email body
        body = f"""
        Dear {contact.name},
        
        Thank you for reaching out to me. I have received your message and will get back to you within 24-48 hours.
        
        Here's a copy of your message:
        
        {contact.message}
        
        Best regards,
        Arnetrice Smith
        Data-Driven Solutions Provider
        arnetrice.com
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, contact.email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

async def send_notification_email(subject: str, message: str, to_email: Optional[str] = None) -> bool:
    """
    Send general notification email to admin or specified recipient
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = to_email or settings.SMTP_USERNAME  # Default to admin email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, to_email or settings.SMTP_USERNAME, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False

async def send_confirmation_email(to_email: str, name: str, subject: str, message: str) -> bool:
    """
    Send confirmation email to customer
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Create professional email body
        body = f"""
        Dear {name},
        
        {message}
        
        If you have any questions or need immediate assistance, please don't hesitate to reach out:
        
        Email: hello@arnetrice.com
        Phone: (555) 123-4567
        Website: https://arnetrice.com
        
        Best regards,
        Arnetrice Smith
        Data-Driven Solutions Provider
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, to_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False

