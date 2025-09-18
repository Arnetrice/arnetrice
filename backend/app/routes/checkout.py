"""
Enhanced Checkout Routes with Multi-Provider Support
Supports Stripe and PayPal payment processing with backward compatibility
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime

from ..database import get_db
from ..models import ClientSubmission
from ..schemas import ClientSubmissionCreate, ClientSubmissionUpdate
from ..schemas.payment import CheckoutRequest, CheckoutResponse, WebhookEvent
from ..config import settings
from ..utils.email import send_notification_email, send_confirmation_email
from ..services.payment_service import PaymentServiceFactory, PaymentProvider as ServiceProvider

# Try to import new models, fallback to legacy if not available
try:
    from ..models_payment import (
        Customer, Subscription, SubscriptionItem, Payment,
        PaymentMethod, Invoice, InvoiceItem, Product, WebhookEvent as WebhookEventModel,
        PaymentProvider, PaymentStatus, SubscriptionStatus
    )
    NEW_MODELS_AVAILABLE = True
except ImportError:
    NEW_MODELS_AVAILABLE = False

router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "frontend", "templates"))

# Updated plan configuration with correct price IDs from env
PLAN_CONFIG = {
    "starter": {
        "name": "Starter Plan",
        "price": 199,
        "monthly_price_id": os.getenv('STRIPE_STARTER_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_STARTER_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_STARTER_SETUP_PRICE_ID'),
        "features": [
            "Data Analysis Dashboard",
            "Monthly Reports",
            "Basic Analytics",
            "Email Support"
        ]
    },
    "growth": {
        "name": "Growth Plan",
        "price": 499,
        "monthly_price_id": os.getenv('STRIPE_GROWTH_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_GROWTH_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_GROWTH_SETUP_PRICE_ID'),
        "features": [
            "Advanced Analytics",
            "Custom Dashboards",
            "BI Integration",
            "Weekly Reports",
            "Priority Support"
        ]
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price": 999,
        "monthly_price_id": os.getenv('STRIPE_ENTERPRISE_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_ENTERPRISE_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_ENTERPRISE_SETUP_PRICE_ID'),
        "features": [
            "Custom Solutions",
            "Dedicated Support",
            "Advanced Security",
            "Custom Integrations"
        ]
    }
}

ADD_ONS = [
    {
        "id": "advanced_ai_analytics",
        "name": "Advanced AI Analytics",
        "price": 99,
        "monthly_price_id": os.getenv('STRIPE_ADVANCED_AI_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_ADVANCED_AI_ANNUAL_PRICE_ID')
    },
    {
        "id": "specialized_bi_dashboards",
        "name": "Specialized BI Dashboards",
        "price": 99,
        "monthly_price_id": os.getenv('STRIPE_BI_DASHBOARDS_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_BI_DASHBOARDS_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_BI_DASHBOARDS_SETUP_PRICE_ID')
    },
    {
        "id": "ai_powered_websites",
        "name": "AI Powered Websites",
        "price": 49,
        "monthly_price_id": os.getenv('STRIPE_AI_WEBSITES_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_AI_WEBSITES_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_AI_WEBSITES_SETUP_PRICE_ID')
    },
    {
        "id": "custom_applications",
        "name": "Custom Applications",
        "price": 99,
        "monthly_price_id": os.getenv('STRIPE_CUSTOM_APPS_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_CUSTOM_APPS_ANNUAL_PRICE_ID'),
        "setup_price_id": os.getenv('STRIPE_CUSTOM_APPS_SETUP_PRICE_ID')
    },
    {
        "id": "text_alerts",
        "name": "Text Alerts",
        "price": 29,
        "monthly_price_id": os.getenv('STRIPE_TEXT_ALERTS_MONTHLY_PRICE_ID'),
        "annual_price_id": os.getenv('STRIPE_TEXT_ALERTS_ANNUAL_PRICE_ID')
    }
]

@router.get("/checkout-starter", response_class=HTMLResponse)
async def checkout_starter(request: Request):
    """Starter plan checkout page"""
    return templates.TemplateResponse("checkout-starter.html", {
        "request": request,
        "title": "Checkout - Starter Plan"
    })

@router.get("/checkout-growth", response_class=HTMLResponse)
async def checkout_growth(request: Request):
    """Growth plan checkout page"""
    return templates.TemplateResponse("checkout-growth.html", {
        "request": request,
        "title": "Checkout - Growth Plan"
    })

@router.get("/enterprise-quote", response_class=HTMLResponse)
async def enterprise_quote(request: Request):
    """Enterprise plan quote request page"""
    return templates.TemplateResponse("enterprise-quote.html", {
        "request": request,
        "plan": "enterprise",
        "title": "Enterprise Quote Request"
    })

@router.get("/payment-pending", response_class=HTMLResponse)
async def payment_pending(
    request: Request,
    transaction_id: str = None,
    method: str = None
):
    """Payment pending status page for bank transfers"""
    return templates.TemplateResponse("payment-pending.html", {
        "request": request,
        "transaction_id": transaction_id,
        "payment_method": method,
        "title": "Payment Pending"
    })

@router.post("/api/checkout/create-session", response_model=CheckoutResponse)
async def create_checkout_session(
    checkout_request: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Create payment checkout session with selected provider"""
    try:
        # Validate policies acceptance
        if not checkout_request.accept_policies:
            raise HTTPException(status_code=400, detail="Must accept terms and policies")

        # Determine payment provider (default to Stripe if not specified)
        provider = checkout_request.payment_provider or "stripe"

        # Create legacy submission for backward compatibility
        legacy_submission = ClientSubmissionCreate(
            name=checkout_request.name,
            email=checkout_request.email,
            phone=checkout_request.phone,
            company=checkout_request.company,
            plan=checkout_request.plan.value,
            payment_frequency=checkout_request.billing_cycle.value,
            add_ons=json.dumps(checkout_request.add_ons) if checkout_request.add_ons else None,
            accept_policies=checkout_request.accept_policies,
            save_card=checkout_request.save_card
        )

        # Save legacy submission to database
        db_submission = ClientSubmission(**legacy_submission.dict())
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)

        # Handle new models if available
        if NEW_MODELS_AVAILABLE:
            # Check if customer exists in new schema
            customer = db.query(Customer).filter_by(email=checkout_request.email).first()
            if not customer:
                # Create new customer
                customer = Customer(
                    name=checkout_request.name,
                    email=checkout_request.email,
                    phone=checkout_request.phone,
                    company=checkout_request.company
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)

        if checkout_request.plan in ["starter", "growth"]:
            # Use payment service based on selected provider
            try:
                if provider == "stripe":
                    payment_service = PaymentServiceFactory.create_service(ServiceProvider.STRIPE)
                elif provider == "paypal":
                    payment_service = PaymentServiceFactory.create_service(ServiceProvider.PAYPAL)
                elif provider == "bank_transfer":
                    payment_service = PaymentServiceFactory.create_service(ServiceProvider.BANK_TRANSFER)
                else:
                    payment_service = PaymentServiceFactory.get_default_service()
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Unsupported payment provider: {provider}")

            customer_data = {
                'name': checkout_request.name,
                'email': checkout_request.email,
                'phone': checkout_request.phone,
                'company': checkout_request.company
            }

            # Prepare additional parameters for bank transfer
            session_kwargs = {
                'plan_id': checkout_request.plan.value,
                'billing_cycle': checkout_request.billing_cycle.value,
                'add_ons': checkout_request.add_ons or [],
                'customer_data': customer_data
            }

            # Add bank info if it's a bank transfer
            if provider == "bank_transfer" and checkout_request.bank_info:
                session_kwargs['bank_info'] = checkout_request.bank_info

            result = payment_service.create_checkout_session(**session_kwargs)

            if result.success:
                # Update submission with payment details
                db_submission.stripe_session_id = result.session_id

                # Create subscription in new schema if available
                if NEW_MODELS_AVAILABLE and customer:
                    product = db.query(Product).filter_by(
                        sku=f"HOSTING_{checkout_request.plan.upper()}"
                    ).first()

                    if product:
                        subscription = Subscription(
                            customer_id=customer.id,
                            status=SubscriptionStatus.INACTIVE,
                            billing_cycle=checkout_request.billing_cycle.value,
                            start_date=datetime.utcnow(),
                            total_amount=product.base_price
                        )

                        if provider == "paypal":
                            subscription.paypal_subscription_id = result.session_id
                        elif provider == "bank_transfer":
                            # For bank transfers, store the transaction ID in a custom field
                            # We'll need to add this field to the Subscription model
                            subscription.custom_metadata = {"bank_transfer_id": result.session_id}
                        else:
                            subscription.stripe_subscription_id = result.session_id

                        db.add(subscription)
                        db.commit()

                db.commit()

                return CheckoutResponse(
                    success=True,
                    checkout_url=result.checkout_url,
                    session_id=result.session_id,
                    provider=provider
                )
            else:
                # Clean up database entry if payment session failed
                db.delete(db_submission)
                db.commit()
                return CheckoutResponse(
                    success=False,
                    error=result.error,
                    provider=provider
                )

        else:
            # Enterprise - no payment session needed
            return CheckoutResponse(
                success=True,
                checkout_url=f"/thank-you-enterprise?submission_id={db_submission.id}",
                provider="none"
            )

    except Exception as e:
        if 'db_submission' in locals():
            db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/checkout/enterprise-submit")
async def submit_enterprise_quote(
    submission: ClientSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit enterprise quote request"""
    try:
        # Save submission to database
        db_submission = ClientSubmission(**submission.dict())
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)

        # Send notification emails
        await send_notification_email(
            subject=f"New Enterprise Quote Request - {submission.name}",
            message=f"""
            New enterprise quote request received:

            Name: {submission.name}
            Email: {submission.email}
            Company: {submission.company or 'Not provided'}
            Requirements: {submission.needs_requirements or 'Not provided'}

            Submission ID: {db_submission.id}
            Date: {db_submission.created_at}
            """
        )

        await send_confirmation_email(
            to_email=submission.email,
            name=submission.name,
            subject="Enterprise Quote Request Received",
            message=f"""
            Thank you for your enterprise quote request, {submission.name}!

            We have received your request and will follow up within 24 hours.

            Our team will review your requirements and provide a customized solution.
            """
        )

        return {"message": "Enterprise quote request submitted successfully", "submission_id": db_submission.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/checkout/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle payment provider webhooks (Stripe, PayPal, etc.)"""
    payload = await request.body()
    signature = request.headers.get('stripe-signature') or request.headers.get('paypal-transmission-sig')

    try:
        # Use payment service to verify and handle webhook
        payment_service = PaymentServiceFactory.get_default_service()

        # Verify webhook authenticity
        if not payment_service.verify_webhook(payload, signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Parse event data
        event_data = json.loads(payload.decode('utf-8'))

        # Store webhook event if new models available
        if NEW_MODELS_AVAILABLE:
            existing_event = db.query(WebhookEventModel).filter_by(
                event_id=event_data.get('id'),
                provider=PaymentProvider.STRIPE
            ).first()

            if existing_event:
                return {"status": "already_processed"}

            webhook_event = WebhookEventModel(
                provider=PaymentProvider.STRIPE,
                event_id=event_data.get('id'),
                event_type=event_data.get('type'),
                payload=event_data,
                processed=False
            )
            db.add(webhook_event)
            db.commit()

        # Process the webhook event
        result = payment_service.handle_webhook_event(event_data)

        if result['processed']:
            await handle_webhook_result(result, db)
            if NEW_MODELS_AVAILABLE and 'webhook_event' in locals():
                webhook_event.processed = True
                webhook_event.processed_at = datetime.utcnow()
                webhook_event.response = result

        db.commit()

        return {"status": "success", "event_type": result['event_type'], "processed": result['processed']}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        if NEW_MODELS_AVAILABLE and 'webhook_event' in locals():
            webhook_event.failed = True
            webhook_event.failure_reason = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

async def handle_webhook_result(result: Dict[str, Any], db: Session):
    """Handle the processed webhook result with backward compatibility"""
    action = result.get('action')

    if action == 'subscription_activated':
        # Handle successful subscription activation
        session_id = result.get('session_id')
        customer_email = result.get('customer_email')
        subscription_id = result.get('subscription_id')
        plan_id = result.get('plan_id')
        billing_cycle = result.get('billing_cycle')

        # Update legacy submission
        db_submission = db.query(ClientSubmission).filter(
            ClientSubmission.stripe_session_id == session_id
        ).first()

        if db_submission:
            # Update submission with subscription details
            db_submission.payment_status = "completed"
            db_submission.stripe_subscription_id = subscription_id
            db_submission.subscription_status = "active"

            # Update new schema if available
            if NEW_MODELS_AVAILABLE:
                subscription = db.query(Subscription).filter_by(
                    stripe_subscription_id=session_id
                ).first()

                if subscription:
                    subscription.status = SubscriptionStatus.ACTIVE
                    subscription.current_period_start = datetime.utcnow()
                    subscription.stripe_subscription_id = subscription_id

            db.commit()

            # Send confirmation email
            plan_name = PLAN_CONFIG.get(plan_id, {}).get('name', plan_id.title())
            await send_confirmation_email(
                to_email=customer_email,
                name=db_submission.name,
                subject=f"Welcome to {plan_name}! Your subscription is active",
                message=f"""
                Thank you for choosing Arnetrice Smith, {db_submission.name}!

                Your {plan_name} subscription is now active and ready to use.

                Plan Details:
                - Plan: {plan_name}
                - Billing: {billing_cycle.title()}
                - Add-ons: {', '.join(result.get('add_ons', [])) if result.get('add_ons') else 'None'}

                What's Next:
                1. You'll receive setup instructions within 24 hours
                2. Our team will contact you to schedule onboarding
                3. Access to your dashboard will be provided soon

                Questions? Reply to this email or contact our support team.

                Welcome aboard!
                Arnetrice Smith Team
                """
            )

            # Send internal notification
            await send_notification_email(
                subject=f"New Subscription Activated - {plan_name}",
                message=f"""
                New subscription activated:

                Customer: {db_submission.name} ({customer_email})
                Plan: {plan_name}
                Billing: {billing_cycle}
                Add-ons: {', '.join(result.get('add_ons', [])) if result.get('add_ons') else 'None'}
                Subscription ID: {subscription_id}
                Session ID: {session_id}

                Action Required: Set up customer account and send onboarding materials.
                """
            )

    elif action == 'payment_failed':
        # Handle failed payment
        subscription_id = result.get('subscription_id')
        customer_email = result.get('customer_email')

        # Find submission and potentially notify customer
        db_submission = db.query(ClientSubmission).filter(
            ClientSubmission.stripe_subscription_id == subscription_id
        ).first()

        if db_submission:
            db_submission.payment_status = "failed"
            db.commit()

            # Send payment failure notification
            await send_confirmation_email(
                to_email=customer_email,
                name=db_submission.name,
                subject="Payment Issue - Action Required",
                message=f"""
                Hi {db_submission.name},

                We encountered an issue processing your recent payment for your Arnetrice Smith subscription.

                Please update your payment method to ensure uninterrupted service.

                If you have questions, please contact our support team.

                Thank you,
                Arnetrice Smith Team
                """
            )

@router.get("/api/checkout/payment-methods")
async def get_payment_methods():
    """Get available payment methods and their status"""
    return {
        "methods": [
            {
                "id": "stripe",
                "name": "Credit/Debit Card",
                "description": "Pay securely with Stripe",
                "enabled": bool(settings.STRIPE_SECRET_KEY),
                "icon": "credit-card"
            },
            {
                "id": "paypal",
                "name": "PayPal",
                "description": "Pay with PayPal account or card",
                "enabled": bool(os.getenv('PAYPAL_CLIENT_ID')) and os.getenv('PAYPAL_CLIENT_ID') != 'your_paypal_client_id_here',
                "icon": "paypal"
            }
        ]
    }

@router.get("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request, session_id: str = None):
    """Thank you page for paid plans"""
    return templates.TemplateResponse("thank-you.html", {
        "request": request,
        "session_id": session_id,
        "plan_type": "paid",
        "title": "Thank You - Payment Successful"
    })

@router.get("/thank-you-enterprise", response_class=HTMLResponse)
async def thank_you_enterprise(request: Request, submission_id: int = None):
    """Thank you page for enterprise quote"""
    return templates.TemplateResponse("thank-you.html", {
        "request": request,
        "submission_id": submission_id,
        "plan_type": "enterprise",
        "title": "Thank You - Quote Request Received"
    })

# Legacy endpoints for backward compatibility
@router.get("/api/plans")
async def get_plans():
    """Get available plans with current pricing"""
    return {
        "plans": PLAN_CONFIG,
        "addons": ADD_ONS
    }