"""Contact form email send. Graceful fallback when SMTP not configured."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import get_settings


logger = logging.getLogger("arnetrice.contact")


def send_contact_email(
    name: str,
    email: str,
    subject: str,
    message: str,
) -> tuple[bool, str | None]:
    """Send a contact-form submission via SMTP.

    Returns (success, error_or_mode).
    - If SMTP is not configured (`SMTP_HOST` empty), logs to stderr and
      returns (True, "log-only") — dev mode.
    - If SMTP is configured and send succeeds: returns (True, None).
    - If SMTP send fails: returns (False, error message).
    """
    settings = get_settings()
    sender = settings.contact_email_from or settings.smtp_user

    if not settings.smtp_host:
        logger.info(
            "[contact log-only] from=%r <%s> subject=%r\n%s",
            name, email, subject, message,
        )
        return True, "log-only"

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = settings.contact_email_to
    msg["Reply-To"] = email
    msg["Subject"] = f"[arnetrice.com] {subject or 'Contact form submission'}"
    msg.set_content(
        f"From: {name} <{email}>\n"
        f"Subject: {subject or '(no subject)'}\n\n"
        f"{message}\n"
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except Exception as exc:
        logger.exception("contact email send failed")
        return False, str(exc)

    return True, None
