from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any
import stripe
import json
import os

from ..database import get_db
from ..models import ClientSubmission
from ..schemas import ClientSubmissionCreate, ClientSubmissionUpdate
from ..schemas.payment import CheckoutRequest, CheckoutResponse, WebhookEvent
from ..config import settings
from ..utils.email import send_notification_email, send_confirmation_email
from ..services.payment_service import PaymentServiceFactory

router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "frontend", "templates"))

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

PLAN_CONFIG = {
    "starter": {
        "name": "Starter Plan",
        "price": 199,
        "stripe_price_id": settings.STRIPE_STARTER_PRICE_ID,
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
        "stripe_price_id": settings.STRIPE_GROWTH_PRICE_ID,
        "features": [
            "Advanced Analytics",
            "Custom Dashboards",
            "BI Integration",
            "Weekly Reports",
            "Priority Support"
        ]
    }
}

ADD_ONS = [
    {"id": "advanced_ai_analytics", "name": "Advanced AI Analytics", "price": 99},
    {"id": "specialized_bi_dashboards", "name": "Specialized BI Dashboards", "price": 99},
    {"id": "ai_powered_websites", "name": "AI Powered Websites", "price": 49},
    {"id": "custom_applications", "name": "Custom Applications", "price": 99}
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

@router.post("/api/checkout/create-session", response_model=CheckoutResponse)
async def create_checkout_session(
    checkout_request: CheckoutRequest,
    db: Session = Depends(get_db)
):
    """Create payment checkout session using the payment service abstraction"""
    try:
        # Validate that policies are accepted
        if not checkout_request.accept_policies:
            raise HTTPException(status_code=400, detail="Must accept terms and policies")
        
        # Convert to legacy format for database compatibility
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
        
        # Save submission to database
        db_submission = ClientSubmission(**legacy_submission.dict())
        db.add(db_submission)
        db.commit()
        db.refresh(db_submission)
        
        if checkout_request.plan in ["starter", "growth"]:
            # Use payment service to create checkout session
            payment_service = PaymentServiceFactory.get_default_service()
            
            customer_data = {
                'name': checkout_request.name,
                'email': checkout_request.email,
                'phone': checkout_request.phone,
                'company': checkout_request.company
            }
            
            result = payment_service.create_checkout_session(
                plan_id=checkout_request.plan.value,
                billing_cycle=checkout_request.billing_cycle.value,
                add_ons=checkout_request.add_ons,
                customer_data=customer_data
            )
            
            if result.success:
                # Update submission with payment details
                db_submission.stripe_session_id = result.session_id
                db.commit()
                
                return CheckoutResponse(
                    success=True,
                    checkout_url=result.checkout_url,
                    session_id=result.session_id
                )
            else:
                # Clean up database entry if payment session failed
                db.delete(db_submission)
                db.commit()
                return CheckoutResponse(success=False, error=result.error)
            
        else:
            # Enterprise - no payment session needed
            return CheckoutResponse(
                success=True,
                checkout_url=f"/thank-you-enterprise?submission_id={db_submission.id}"
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
        import json
        event_data = json.loads(payload.decode('utf-8'))
        
        # Process the webhook event
        result = payment_service.handle_webhook_event(event_data)
        
        if result['processed']:
            await handle_webhook_result(result, db)
        
        return {"status": "success", "event_type": result['event_type'], "processed": result['processed']}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

async def handle_webhook_result(result: Dict[str, Any], db: Session):
    """Handle the processed webhook result"""
    action = result.get('action')
    
    if action == 'subscription_activated':
        # Handle successful subscription activation
        session_id = result.get('session_id')
        customer_email = result.get('customer_email')
        subscription_id = result.get('subscription_id')
        plan_id = result.get('plan_id')
        billing_cycle = result.get('billing_cycle')
        
        # Find the submission by session_id
        db_submission = db.query(ClientSubmission).filter(
            ClientSubmission.stripe_session_id == session_id
        ).first()
        
        if db_submission:
            # Update submission with subscription details
            db_submission.payment_status = "completed"
            db_submission.stripe_subscription_id = subscription_id
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
    
    elif action == 'payment_succeeded':
        # Handle successful recurring payment
        subscription_id = result.get('subscription_id')
        amount_paid = result.get('amount_paid')
        customer_email = result.get('customer_email')
        
        # Find submission by subscription_id
        db_submission = db.query(ClientSubmission).filter(
            ClientSubmission.stripe_subscription_id == subscription_id
        ).first()
        
        if db_submission:
            # Could log payment history or send receipt email here
            pass
    
    elif action == 'payment_failed':
        # Handle failed payment
        subscription_id = result.get('subscription_id')
        customer_email = result.get('customer_email')
        
        # Find submission and potentially notify customer
        db_submission = db.query(ClientSubmission).filter(
            ClientSubmission.stripe_subscription_id == subscription_id
        ).first()
        
        if db_submission:
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