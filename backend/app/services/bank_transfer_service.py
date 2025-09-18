"""
Bank Transfer Payment Service
Handles ACH bank transfers for payment processing
"""
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .payment_service import PaymentService, PaymentResult


class BankTransferPaymentService(PaymentService):
    """Bank transfer implementation of payment service"""

    def __init__(self):
        # Bank transfer doesn't require API keys like Stripe/PayPal
        pass

    def create_checkout_session(self,
                              plan_id: str,
                              billing_cycle: str,
                              add_ons: List[str],
                              customer_data: Dict[str, Any],
                              bank_info: Dict[str, Any] = None) -> PaymentResult:
        """
        Create a bank transfer 'session' - really just validation and record creation
        """
        try:
            # Generate a unique transaction ID for tracking
            transaction_id = f"ach_{uuid.uuid4().hex[:16]}"

            # Validate bank info if provided
            if bank_info:
                required_fields = ['routing_number', 'account_number', 'account_type']
                for field in required_fields:
                    if not bank_info.get(field):
                        return PaymentResult(
                            success=False,
                            error=f"Missing required bank information: {field}"
                        )

                # Basic validation for routing number (9 digits)
                routing_number = bank_info.get('routing_number', '').replace('-', '').replace(' ', '')
                if not routing_number.isdigit() or len(routing_number) != 9:
                    return PaymentResult(
                        success=False,
                        error="Routing number must be exactly 9 digits"
                    )

                account_number = bank_info.get('account_number', '').replace('-', '').replace(' ', '')
                if not account_number or len(account_number) < 4:
                    return PaymentResult(
                        success=False,
                        error="Account number is required and must be at least 4 digits"
                    )

            # For bank transfers, we return a success with a special URL that shows pending status
            return PaymentResult(
                success=True,
                session_id=transaction_id,
                checkout_url=f"/payment-pending?transaction_id={transaction_id}&method=bank_transfer"
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                error=f"Bank transfer setup failed: {str(e)}"
            )

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """
        Bank transfers don't use webhooks in the same way as Stripe/PayPal
        This would be used for ACH notification webhooks if integrated with a bank API
        """
        # For now, always return True as we don't have real bank webhooks
        return True

    def handle_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank transfer status updates
        In a real implementation, this would process ACH status notifications
        """
        return {
            'processed': True,
            'action': 'bank_transfer_notification',
            'event_type': event_data.get('type', 'unknown'),
            'transaction_id': event_data.get('transaction_id'),
            'status': event_data.get('status', 'pending')
        }

    def calculate_processing_fee(self, amount: float) -> float:
        """Calculate processing fee for bank transfer (typically $0)"""
        return 0.0

    def get_processing_time(self) -> str:
        """Get expected processing time for bank transfers"""
        return "1-3 business days"

    def format_account_display(self, account_number: str) -> str:
        """Format account number for display (mask most digits)"""
        if len(account_number) <= 4:
            return "****"
        return f"****{account_number[-4:]}"