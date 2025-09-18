"""
PayPal Payment Service Implementation
Supports subscriptions, one-time payments, and webhooks
"""
import os
import json
import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..config import settings
from .payment_service import PaymentService, PaymentResult, PaymentProvider

class PayPalPaymentService(PaymentService):
    """PayPal implementation of payment service"""

    def __init__(self):
        self.client_id = os.getenv('PAYPAL_CLIENT_ID', '')
        self.client_secret = os.getenv('PAYPAL_CLIENT_SECRET', '')
        self.webhook_id = os.getenv('PAYPAL_WEBHOOK_ID', '')

        # Set environment (sandbox or live)
        self.environment = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')
        if self.environment == 'live':
            self.base_url = 'https://api-m.paypal.com'
        else:
            self.base_url = 'https://api-m.sandbox.paypal.com'

        # Plan mapping
        self.plan_ids = {
            'starter': {
                'monthly': os.getenv('PAYPAL_STARTER_MONTHLY_PLAN_ID', ''),
                'annual': os.getenv('PAYPAL_STARTER_ANNUAL_PLAN_ID', '')
            },
            'growth': {
                'monthly': os.getenv('PAYPAL_GROWTH_MONTHLY_PLAN_ID', ''),
                'annual': os.getenv('PAYPAL_GROWTH_ANNUAL_PLAN_ID', '')
            },
            'enterprise': {
                'monthly': os.getenv('PAYPAL_ENTERPRISE_MONTHLY_PLAN_ID', ''),
                'annual': os.getenv('PAYPAL_ENTERPRISE_ANNUAL_PLAN_ID', '')
            }
        }

        # Add-on product IDs
        self.addon_product_ids = {
            'advanced_ai_analytics': os.getenv('PAYPAL_ADVANCED_AI_PRODUCT_ID', ''),
            'ai_powered_websites': os.getenv('PAYPAL_AI_WEBSITES_PRODUCT_ID', ''),
            'custom_applications': os.getenv('PAYPAL_CUSTOM_APPS_PRODUCT_ID', ''),
            'text_alerts': os.getenv('PAYPAL_TEXT_ALERTS_PRODUCT_ID', '')
        }

        # Cache for access token
        self._access_token = None
        self._token_expiry = None

    def get_access_token(self) -> str:
        """Get PayPal OAuth2 access token"""
        # Check if cached token is still valid
        if self._access_token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._access_token

        # Get new token
        auth_string = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            'Authorization': f'Basic {auth_string}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            headers=headers,
            data='grant_type=client_credentials'
        )

        if response.status_code == 200:
            data = response.json()
            self._access_token = data['access_token']
            # Set expiry with 5-minute buffer
            self._token_expiry = datetime.utcnow() + timedelta(seconds=data['expires_in'] - 300)
            return self._access_token
        else:
            raise Exception(f"Failed to get PayPal access token: {response.text}")

    def create_product(self, name: str, description: str, category: str = "SOFTWARE") -> str:
        """Create a product in PayPal"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

        product_data = {
            "name": name,
            "description": description,
            "type": "SERVICE",
            "category": category
        }

        response = requests.post(
            f"{self.base_url}/v1/catalogs/products",
            headers=headers,
            json=product_data
        )

        if response.status_code == 201:
            return response.json()['id']
        else:
            raise Exception(f"Failed to create PayPal product: {response.text}")

    def create_plan(self, product_id: str, name: str, price: float, billing_cycle: str) -> str:
        """Create a subscription plan in PayPal"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

        # Determine billing frequency
        if billing_cycle == 'monthly':
            frequency = {
                "interval_unit": "MONTH",
                "interval_count": 1
            }
        else:  # annual
            frequency = {
                "interval_unit": "YEAR",
                "interval_count": 1
            }

        plan_data = {
            "product_id": product_id,
            "name": name,
            "description": f"{name} - {billing_cycle.title()} Billing",
            "billing_cycles": [
                {
                    "frequency": frequency,
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,  # 0 means infinite
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": str(price),
                            "currency_code": "USD"
                        }
                    }
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee": {
                    "value": "0",
                    "currency_code": "USD"
                },
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 3
            }
        }

        response = requests.post(
            f"{self.base_url}/v1/billing/plans",
            headers=headers,
            json=plan_data
        )

        if response.status_code == 201:
            plan_id = response.json()['id']
            # Activate the plan
            self.activate_plan(plan_id)
            return plan_id
        else:
            raise Exception(f"Failed to create PayPal plan: {response.text}")

    def activate_plan(self, plan_id: str):
        """Activate a PayPal subscription plan"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f"{self.base_url}/v1/billing/plans/{plan_id}/activate",
            headers=headers
        )

        if response.status_code not in [200, 204]:
            raise Exception(f"Failed to activate PayPal plan: {response.text}")

    def create_checkout_session(self,
                              plan_id: str,
                              billing_cycle: str,
                              add_ons: List[str],
                              customer_data: Dict[str, Any]) -> PaymentResult:
        """Create PayPal subscription"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }

            # Get the plan ID
            if plan_id not in self.plan_ids or billing_cycle not in self.plan_ids[plan_id]:
                return PaymentResult(success=False, error=f"Invalid plan or billing cycle: {plan_id}, {billing_cycle}")

            paypal_plan_id = self.plan_ids[plan_id][billing_cycle]

            if not paypal_plan_id:
                return PaymentResult(success=False, error="PayPal plan not configured")

            # Create subscription
            subscription_data = {
                "plan_id": paypal_plan_id,
                "subscriber": {
                    "name": {
                        "given_name": customer_data.get('name', '').split(' ')[0],
                        "surname": customer_data.get('name', '').split(' ')[-1] if ' ' in customer_data.get('name', '') else ''
                    },
                    "email_address": customer_data.get('email')
                },
                "application_context": {
                    "brand_name": "Arnetrice Smith",
                    "locale": "en-US",
                    "shipping_preference": "NO_SHIPPING",
                    "user_action": "SUBSCRIBE_NOW",
                    "payment_method": {
                        "payer_selected": "PAYPAL",
                        "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                    },
                    "return_url": f"{settings.BASE_URL}/thank-you?provider=paypal",
                    "cancel_url": f"{settings.BASE_URL}/checkout-{plan_id}"
                },
                "custom_id": json.dumps({
                    "plan_id": plan_id,
                    "billing_cycle": billing_cycle,
                    "add_ons": add_ons,
                    "customer_name": customer_data.get('name'),
                    "customer_phone": customer_data.get('phone'),
                    "company": customer_data.get('company')
                })
            }

            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions",
                headers=headers,
                json=subscription_data
            )

            if response.status_code == 201:
                data = response.json()
                # Find the approval link
                approval_url = None
                for link in data.get('links', []):
                    if link['rel'] == 'approve':
                        approval_url = link['href']
                        break

                return PaymentResult(
                    success=True,
                    checkout_url=approval_url,
                    session_id=data['id']
                )
            else:
                return PaymentResult(success=False, error=f"PayPal API error: {response.text}")

        except Exception as e:
            return PaymentResult(success=False, error=f"Unexpected error: {str(e)}")

    def verify_webhook(self, payload: bytes, headers: Dict[str, str]) -> bool:
        """Verify PayPal webhook signature"""
        try:
            verify_headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }

            verify_data = {
                "auth_algo": headers.get('paypal-auth-algo'),
                "cert_url": headers.get('paypal-cert-url'),
                "transmission_id": headers.get('paypal-transmission-id'),
                "transmission_sig": headers.get('paypal-transmission-sig'),
                "transmission_time": headers.get('paypal-transmission-time'),
                "webhook_id": self.webhook_id,
                "webhook_event": json.loads(payload.decode('utf-8'))
            }

            response = requests.post(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                headers=verify_headers,
                json=verify_data
            )

            if response.status_code == 200:
                return response.json().get('verification_status') == 'SUCCESS'
            return False

        except Exception:
            return False

    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PayPal webhook events"""
        event_type = event_data.get('event_type')
        resource = event_data.get('resource', {})

        result = {'processed': False, 'event_type': event_type}

        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            # Subscription activated
            subscription_id = resource.get('id')
            subscriber = resource.get('subscriber', {})
            custom_data = json.loads(resource.get('custom_id', '{}'))

            result.update({
                'processed': True,
                'action': 'subscription_activated',
                'session_id': subscription_id,
                'customer_email': subscriber.get('email_address'),
                'subscription_id': subscription_id,
                'plan_id': custom_data.get('plan_id'),
                'billing_cycle': custom_data.get('billing_cycle'),
                'add_ons': custom_data.get('add_ons', [])
            })

        elif event_type == 'PAYMENT.SALE.COMPLETED':
            # Payment completed
            subscription_id = resource.get('billing_agreement_id')
            amount = resource.get('amount', {})

            result.update({
                'processed': True,
                'action': 'payment_succeeded',
                'subscription_id': subscription_id,
                'amount_paid': float(amount.get('total', 0)),
                'currency': amount.get('currency', 'USD')
            })

        elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.FAILED':
            # Payment failed
            subscription_id = resource.get('id')

            result.update({
                'processed': True,
                'action': 'payment_failed',
                'subscription_id': subscription_id
            })

        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            # Subscription cancelled
            subscription_id = resource.get('id')

            result.update({
                'processed': True,
                'action': 'subscription_cancelled',
                'subscription_id': subscription_id
            })

        elif event_type == 'BILLING.SUBSCRIPTION.SUSPENDED':
            # Subscription suspended (past due)
            subscription_id = resource.get('id')

            result.update({
                'processed': True,
                'action': 'subscription_suspended',
                'subscription_id': subscription_id
            })

        return result

    def cancel_subscription(self, subscription_id: str, reason: str = "Customer requested") -> bool:
        """Cancel a PayPal subscription"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }

            cancel_data = {
                "reason": reason
            }

            response = requests.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
                headers=headers,
                json=cancel_data
            )

            return response.status_code in [200, 204]

        except Exception:
            return False

    def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a PayPal subscription"""
        try:
            headers = {
                'Authorization': f'Bearer {self.get_access_token()}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}",
                headers=headers
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception:
            return None