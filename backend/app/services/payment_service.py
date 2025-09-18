"""
Payment Service Abstraction Layer
Supports multiple payment providers (Stripe, PayPal, etc.)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
import os
import stripe
from ..config import settings

class PaymentProvider(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class PaymentResult:
    """Standard payment result across all providers"""
    def __init__(self, success: bool, checkout_url: str = None, session_id: str = None, error: str = None):
        self.success = success
        self.checkout_url = checkout_url
        self.session_id = session_id
        self.error = error

class PaymentService(ABC):
    """Abstract base class for payment services"""
    
    @abstractmethod
    def create_checkout_session(self, 
                              plan_id: str, 
                              billing_cycle: str, 
                              add_ons: List[str], 
                              customer_data: Dict[str, Any]) -> PaymentResult:
        """Create a checkout session with the payment provider"""
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify webhook authenticity"""
        pass
    
    @abstractmethod
    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook events"""
        pass

class StripePaymentService(PaymentService):
    """Stripe implementation of payment service"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
        # Plan pricing mapping - updated to match your .env.prod structure
        self.plan_prices = {
            'starter': {
                'monthly': os.getenv('STRIPE_STARTER_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_STARTER_ANNUAL_PRICE_ID')
            },
            'growth': {
                'monthly': os.getenv('STRIPE_GROWTH_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_GROWTH_ANNUAL_PRICE_ID')
            },
            'enterprise': {
                'monthly': os.getenv('STRIPE_ENTERPRISE_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_ENTERPRISE_ANNUAL_PRICE_ID')
            }
        }
        
        # Add-on pricing mapping - updated to match your .env.prod structure
        self.addon_prices = {
            'advanced_ai_analytics': {
                'monthly': os.getenv('STRIPE_ADVANCED_AI_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_ADVANCED_AI_ANNUAL_PRICE_ID')
            },
            'ai_powered_websites': {
                'monthly': os.getenv('STRIPE_AI_WEBSITES_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_AI_WEBSITES_ANNUAL_PRICE_ID'),
                'setup_fee': os.getenv('STRIPE_AI_WEBSITES_SETUP_PRICE_ID')
            },
            'custom_applications': {
                'monthly': os.getenv('STRIPE_CUSTOM_APPS_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_CUSTOM_APPS_ANNUAL_PRICE_ID'),
                'setup_fee': os.getenv('STRIPE_CUSTOM_APPS_SETUP_PRICE_ID')
            },
            'specialized_bi_dashboards': {
                'monthly': os.getenv('STRIPE_BI_DASHBOARDS_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_BI_DASHBOARDS_ANNUAL_PRICE_ID'),
                'setup_fee': os.getenv('STRIPE_BI_DASHBOARDS_SETUP_PRICE_ID')
            },
            'text_alerts': {
                'monthly': os.getenv('STRIPE_TEXT_ALERTS_MONTHLY_PRICE_ID'),
                'annual': os.getenv('STRIPE_TEXT_ALERTS_ANNUAL_PRICE_ID')
            }
        }
    
    def create_checkout_session(self, 
                              plan_id: str, 
                              billing_cycle: str, 
                              add_ons: List[str], 
                              customer_data: Dict[str, Any]) -> PaymentResult:
        """Create Stripe checkout session"""
        try:
            # Build line items starting with base plan
            line_items = []
            
            # Add base plan
            if plan_id in self.plan_prices and billing_cycle in self.plan_prices[plan_id]:
                line_items.append({
                    'price': self.plan_prices[plan_id][billing_cycle],
                    'quantity': 1
                })
            else:
                return PaymentResult(success=False, error=f"Invalid plan or billing cycle: {plan_id}, {billing_cycle}")
            
            # Add selected add-ons
            for addon in add_ons:
                if addon in self.addon_prices:
                    addon_config = self.addon_prices[addon]
                    
                    # Add recurring subscription
                    if billing_cycle in addon_config:
                        line_items.append({
                            'price': addon_config[billing_cycle],
                            'quantity': 1
                        })
                    
                    # Add one-time setup fee if exists
                    if 'setup_fee' in addon_config:
                        line_items.append({
                            'price': addon_config['setup_fee'],
                            'quantity': 1
                        })
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='subscription',
                success_url=f"{settings.BASE_URL}/thank-you?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.BASE_URL}/checkout-{plan_id}",
                customer_email=customer_data.get('email'),
                metadata={
                    'plan_id': plan_id,
                    'billing_cycle': billing_cycle,
                    'add_ons': ','.join(add_ons),
                    'customer_name': customer_data.get('name', ''),
                    'customer_phone': customer_data.get('phone', ''),
                    'company': customer_data.get('company', '')
                },
                subscription_data={
                    'metadata': {
                        'plan_id': plan_id,
                        'billing_cycle': billing_cycle,
                        'add_ons': ','.join(add_ons)
                    }
                }
            )
            
            return PaymentResult(
                success=True,
                checkout_url=session.url,
                session_id=session.id
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(success=False, error=str(e))
        except Exception as e:
            return PaymentResult(success=False, error=f"Unexpected error: {str(e)}")
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return True
        except (stripe.error.InvalidRequestError, ValueError):
            return False
    
    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        event_type = event_data.get('type')
        event_object = event_data.get('data', {}).get('object', {})
        
        result = {'processed': False, 'event_type': event_type}
        
        if event_type == 'checkout.session.completed':
            # Customer completed payment
            session_id = event_object.get('id')
            customer_email = event_object.get('customer_email')
            subscription_id = event_object.get('subscription')
            metadata = event_object.get('metadata', {})
            
            result.update({
                'processed': True,
                'action': 'subscription_activated',
                'session_id': session_id,
                'customer_email': customer_email,
                'subscription_id': subscription_id,
                'plan_id': metadata.get('plan_id'),
                'billing_cycle': metadata.get('billing_cycle'),
                'add_ons': metadata.get('add_ons', '').split(',') if metadata.get('add_ons') else []
            })
            
        elif event_type == 'invoice.payment_succeeded':
            # Subscription payment successful
            subscription_id = event_object.get('subscription')
            customer_email = event_object.get('customer_email')
            amount_paid = event_object.get('amount_paid', 0) / 100  # Convert from cents
            
            result.update({
                'processed': True,
                'action': 'payment_succeeded',
                'subscription_id': subscription_id,
                'customer_email': customer_email,
                'amount_paid': amount_paid
            })
            
        elif event_type == 'invoice.payment_failed':
            # Subscription payment failed
            subscription_id = event_object.get('subscription')
            customer_email = event_object.get('customer_email')
            
            result.update({
                'processed': True,
                'action': 'payment_failed',
                'subscription_id': subscription_id,
                'customer_email': customer_email
            })
        
        return result

# PayPal implementation moved to separate file
# Import the full implementation
from .paypal_service import PayPalPaymentService
from .bank_transfer_service import BankTransferPaymentService

class PaymentServiceFactory:
    """Factory to create payment service instances"""
    
    @staticmethod
    def create_service(provider: PaymentProvider) -> PaymentService:
        if provider == PaymentProvider.STRIPE:
            return StripePaymentService()
        elif provider == PaymentProvider.PAYPAL:
            return PayPalPaymentService()
        elif provider == PaymentProvider.BANK_TRANSFER:
            return BankTransferPaymentService()
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")
    
    @staticmethod
    def get_default_service() -> PaymentService:
        """Get the default payment service (Stripe for now)"""
        return PaymentServiceFactory.create_service(PaymentProvider.STRIPE)