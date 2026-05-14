from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.deps import base_context, templates
from app.services.email import send_contact_email


router = APIRouter()


@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("pages/contact.html", base_context(request))


@router.post("/contact", response_class=HTMLResponse)
async def contact_submit(
    request: Request,
    name: str = Form(..., min_length=1, max_length=200),
    email: str = Form(..., min_length=3, max_length=200),
    subject: str = Form(default="", max_length=200),
    message: str = Form(..., min_length=1, max_length=10_000),
    honeypot: str = Form(default=""),
):
    ctx = base_context(request)

    # Honeypot — bots fill hidden fields, humans don't. Silently "succeed".
    if honeypot.strip():
        return templates.TemplateResponse("_partials/contact_success.html", ctx)

    # Basic email shape sanity (FastAPI Form already trims; deep validation
    # is the SMTP server's problem).
    if "@" not in email or "." not in email:
        ctx["error_message"] = "That email address doesn't look right. Try again."
        return templates.TemplateResponse(
            "_partials/contact_form.html", ctx, status_code=400
        )

    ok, info = send_contact_email(name=name, email=email, subject=subject, message=message)

    if ok:
        ctx["delivery_mode"] = info  # "log-only" in dev, None in prod
        return templates.TemplateResponse("_partials/contact_success.html", ctx)

    ctx["error_message"] = (
        "Couldn't send the message — please email align@qoat.ai directly. "
        f"({info})"
    )
    return templates.TemplateResponse(
        "_partials/contact_form.html", ctx, status_code=500
    )
