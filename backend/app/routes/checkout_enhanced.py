"""
Enhanced Checkout Routes with Multi-Provider Support
Supports Stripe and PayPal payment processing
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
from ..models_payment import (
    Customer, Subscription, SubscriptionItem, Payment,
    PaymentMethod, Invoice, InvoiceItem, Product, WebhookEvent,
    PaymentProvider, PaymentStatus, SubscriptionStatus
)
from ..schemas.payment import CheckoutRequest, CheckoutResponse, WebhookEvent as WebhookEventSchema
from ..config import settings
from ..utils.email import send_notification_email, send_confirmation_email
from ..services.payment_service import PaymentServiceFactory, PaymentProvider as ServiceProvider
from ..services.paypal_service import PayPalPaymentService

router = APIRouter()

# Initialize templates
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "frontend", "templates"))

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

        # Check if customer exists
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

        # Get product information
        product = db.query(Product).filter_by(
            sku=f"HOSTING_{checkout_request.plan.upper()}"
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Create payment service
        if provider == "paypal":
            payment_service = PayPalPaymentService()
        else:
            payment_service = PaymentServiceFactory.create_service(ServiceProvider.STRIPE)

        # Prepare customer data
        customer_data = {
            'name': checkout_request.name,
            'email': checkout_request.email,
            'phone': checkout_request.phone,
            'company': checkout_request.company
        }

        # Create checkout session with selected provider
        result = payment_service.create_checkout_session(
            plan_id=checkout_request.plan.value,
            billing_cycle=checkout_request.billing_cycle.value,
            add_ons=checkout_request.add_ons or [],
            customer_data=customer_data
        )

        if result.success:
            # Create subscription record (pending activation)
            subscription = Subscription(
                customer_id=customer.id,
                status=SubscriptionStatus.INACTIVE,
                billing_cycle=checkout_request.billing_cycle.value,
                start_date=datetime.utcnow(),
                total_amount=product.base_price
            )

            # Set provider-specific IDs
            if provider == "paypal":
                subscription.paypal_subscription_id = result.session_id
            else:
                subscription.stripe_subscription_id = result.session_id

            db.add(subscription)

            # Add subscription items
            subscription_item = SubscriptionItem(
                subscription_id=subscription.id,
                product_id=product.id,
                quantity=1,
                unit_price=product.base_price
            )
            db.add(subscription_item)

            # Add add-ons if any
            for addon_sku in checkout_request.add_ons or []:
                addon_product = db.query(Product).filter_by(
                    sku=f"ADDON_{addon_sku.upper()}"
                ).first()
                if addon_product:
                    addon_item = SubscriptionItem(
                        subscription_id=subscription.id,
                        product_id=addon_product.id,
                        quantity=1,
                        unit_price=addon_product.base_price
                    )
                    db.add(addon_item)

            db.commit()

            return CheckoutResponse(
                success=True,
                checkout_url=result.checkout_url,
                session_id=result.session_id,
                provider=provider
            )
        else:
            return CheckoutResponse(
                success=False,
                error=result.error,
                provider=provider
            )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/checkout/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    payload = await request.body()

    try:
        # Use payment service to verify and handle webhook
        payment_service = PaymentServiceFactory.create_service(ServiceProvider.STRIPE)

        # Verify webhook authenticity
        if not payment_service.verify_webhook(payload, stripe_signature):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Parse event data
        event_data = json.loads(payload.decode('utf-8'))

        # Check if we've already processed this event
        existing_event = db.query(WebhookEvent).filter_by(
            event_id=event_data.get('id'),
            provider=PaymentProvider.STRIPE
        ).first()

        if existing_event:
            return {"status": "already_processed"}

        # Store webhook event
        webhook_event = WebhookEvent(
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
            await process_payment_event(result, db, PaymentProvider.STRIPE)
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()
            webhook_event.response = result
        else:
            webhook_event.failed = True
            webhook_event.failure_reason = result.get('error', 'Unknown error')

        db.commit()

        return {"status": "success", "event_type": result['event_type']}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        if 'webhook_event' in locals():
            webhook_event.failed = True
            webhook_event.failure_reason = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

@router.post("/api/checkout/webhook/paypal")
async def paypal_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle PayPal webhook events"""
    payload = await request.body()
    headers = dict(request.headers)

    try:
        # Use PayPal service to verify and handle webhook
        payment_service = PayPalPaymentService()

        # Verify webhook authenticity
        if not payment_service.verify_webhook(payload, headers):
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

        # Parse event data
        event_data = json.loads(payload.decode('utf-8'))

        # Check if we've already processed this event
        existing_event = db.query(WebhookEvent).filter_by(
            event_id=event_data.get('id'),
            provider=PaymentProvider.PAYPAL
        ).first()

        if existing_event:
            return {"status": "already_processed"}

        # Store webhook event
        webhook_event = WebhookEvent(
            provider=PaymentProvider.PAYPAL,
            event_id=event_data.get('id'),
            event_type=event_data.get('event_type'),
            payload=event_data,
            processed=False
        )
        db.add(webhook_event)
        db.commit()

        # Process the webhook event
        result = payment_service.handle_webhook_event(event_data)

        if result['processed']:
            await process_payment_event(result, db, PaymentProvider.PAYPAL)
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()
            webhook_event.response = result
        else:
            webhook_event.failed = True
            webhook_event.failure_reason = result.get('error', 'Unknown error')

        db.commit()

        return {"status": "success", "event_type": result['event_type']}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        if 'webhook_event' in locals():
            webhook_event.failed = True
            webhook_event.failure_reason = str(e)
            db.commit()
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

async def process_payment_event(result: Dict[str, Any], db: Session, provider: PaymentProvider):
    """Process payment events from webhooks"""
    action = result.get('action')

    if action == 'subscription_activated':
        # Handle successful subscription activation
        session_id = result.get('session_id')
        subscription_id = result.get('subscription_id')
        customer_email = result.get('customer_email')

        # Find the subscription
        if provider == PaymentProvider.STRIPE:
            subscription = db.query(Subscription).filter_by(
                stripe_subscription_id=session_id
            ).first()
        else:
            subscription = db.query(Subscription).filter_by(
                paypal_subscription_id=session_id
            ).first()

        if subscription:
            # Update subscription status
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = datetime.utcnow()

            # Update external subscription ID
            if provider == PaymentProvider.STRIPE:
                subscription.stripe_subscription_id = subscription_id
            else:
                subscription.paypal_subscription_id = subscription_id

            # Create initial invoice
            invoice = Invoice(
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{subscription.id}",
                status=InvoiceStatus.PAID,
                issue_date=datetime.utcnow(),
                due_date=datetime.utcnow(),
                paid_date=datetime.utcnow(),
                subtotal=subscription.total_amount,
                total_amount=subscription.total_amount,
                paid_amount=subscription.total_amount,
                balance_due=0
            )
            db.add(invoice)

            # Create payment record
            payment = Payment(
                customer_id=subscription.customer_id,
                invoice_id=invoice.id,
                amount=subscription.total_amount,
                status=PaymentStatus.COMPLETED,
                provider=provider,
                processed_at=datetime.utcnow()
            )

            if provider == PaymentProvider.STRIPE:
                payment.stripe_payment_intent_id = result.get('payment_intent_id')
            else:
                payment.paypal_transaction_id = result.get('transaction_id')

            db.add(payment)
            db.commit()

            # Send confirmation emails
            customer = subscription.customer
            await send_confirmation_email(
                to_email=customer.email,
                name=customer.name,
                subject="Subscription Activated - Welcome!",
                message=f"""
                Thank you for subscribing, {customer.name}!

                Your subscription is now active and ready to use.

                Subscription Details:
                - Plan: {result.get('plan_id', '').title()}
                - Billing: {result.get('billing_cycle', '').title()}
                - Payment Method: {provider.value.title()}

                What's Next:
                1. You'll receive setup instructions within 24 hours
                2. Our team will contact you to schedule onboarding
                3. Access to your dashboard will be provided soon

                Thank you for choosing Arnetrice Smith!
                """
            )

    elif action == 'payment_succeeded':
        # Handle successful recurring payment
        subscription_id = result.get('subscription_id')
        amount_paid = result.get('amount_paid', 0)

        # Find subscription by external ID
        if provider == PaymentProvider.STRIPE:
            subscription = db.query(Subscription).filter_by(
                stripe_subscription_id=subscription_id
            ).first()
        else:
            subscription = db.query(Subscription).filter_by(
                paypal_subscription_id=subscription_id
            ).first()

        if subscription:
            # Create payment record
            payment = Payment(
                customer_id=subscription.customer_id,
                amount=amount_paid,
                status=PaymentStatus.COMPLETED,
                provider=provider,
                processed_at=datetime.utcnow(),
                description="Recurring subscription payment"
            )
            db.add(payment)
            db.commit()

    elif action == 'payment_failed':
        # Handle failed payment
        subscription_id = result.get('subscription_id')

        # Find subscription
        if provider == PaymentProvider.STRIPE:
            subscription = db.query(Subscription).filter_by(
                stripe_subscription_id=subscription_id
            ).first()
        else:
            subscription = db.query(Subscription).filter_by(
                paypal_subscription_id=subscription_id
            ).first()

        if subscription:
            # Update subscription status
            subscription.status = SubscriptionStatus.PAST_DUE

            # Create failed payment record
            payment = Payment(
                customer_id=subscription.customer_id,
                amount=subscription.total_amount,
                status=PaymentStatus.FAILED,
                provider=provider,
                failed_at=datetime.utcnow(),
                failure_reason="Payment method declined or insufficient funds"
            )
            db.add(payment)
            db.commit()

            # Send payment failure notification
            customer = subscription.customer
            await send_confirmation_email(
                to_email=customer.email,
                name=customer.name,
                subject="Payment Failed - Action Required",
                message=f"""
                Hi {customer.name},

                We encountered an issue processing your recent payment.

                Please update your payment method to ensure uninterrupted service.

                You can update your payment information at:
                {settings.BASE_URL}/account/billing

                If you have questions, please contact our support team.

                Thank you,
                Arnetrice Smith Team
                """
            )

    elif action == 'subscription_cancelled':
        # Handle subscription cancellation
        subscription_id = result.get('subscription_id')

        # Find subscription
        if provider == PaymentProvider.STRIPE:
            subscription = db.query(Subscription).filter_by(
                stripe_subscription_id=subscription_id
            ).first()
        else:
            subscription = db.query(Subscription).filter_by(
                paypal_subscription_id=subscription_id
            ).first()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            db.commit()

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
                "enabled": bool(os.getenv('PAYPAL_CLIENT_ID')),
                "icon": "paypal"
            }
        ]
    }

@router.get("/api/subscriptions/{customer_email}")
async def get_customer_subscriptions(
    customer_email: str,
    db: Session = Depends(get_db)
):
    """Get all subscriptions for a customer"""
    customer = db.query(Customer).filter_by(email=customer_email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    subscriptions = db.query(Subscription).filter_by(
        customer_id=customer.id
    ).all()

    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email
        },
        "subscriptions": [
            {
                "id": sub.id,
                "status": sub.status.value,
                "billing_cycle": sub.billing_cycle,
                "start_date": sub.start_date,
                "next_billing_date": sub.next_billing_date,
                "total_amount": float(sub.total_amount),
                "provider": "stripe" if sub.stripe_subscription_id else "paypal"
            }
            for sub in subscriptions
        ]
    }