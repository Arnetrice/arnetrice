# Payment System Setup Instructions

## Overview

Your payment system now supports both Stripe and PayPal with a scalable ERP-level database structure. Here's what has been implemented:

### Features Completed:
✅ **ERP-Level Database Schema** - Comprehensive tables for customers, subscriptions, payments, invoices, and audit logs
✅ **Stripe Integration** - Full subscription and checkout flow
✅ **PayPal Integration** - Complete PayPal subscription service
✅ **Multi-Provider Checkout** - Users can choose between Stripe and PayPal
✅ **Webhook Handling** - Secure webhook processing for both providers
✅ **Database Migration Script** - Automated table creation and product seeding

## Next Steps Required

### 1. Database Setup

Run the migration script to create the new payment tables:

```bash
cd C:\Python312\Projects\Arnetrice
python -m backend.app.migrations.create_payment_tables
```

### 2. Stripe Configuration

**CRITICAL**: You currently have Product IDs instead of Price IDs in your `.env.prod` file.

**Steps:**
1. Go to your Stripe Dashboard → Products
2. For each product, create **Price** objects (not just products)
3. Replace the `price_REPLACE_WITH_ACTUAL_PRICE_ID` values in `.env.prod` with actual price IDs

**Example:**
- Instead of: `STRIPE_STARTER_MONTHLY_PRICE_ID=price_REPLACE_WITH_ACTUAL_PRICE_ID`
- Use: `STRIPE_STARTER_MONTHLY_PRICE_ID=price_1AbC2dEfGhIjKlMn`

**Prices to Create:**
```
Starter Plan:
- Monthly: $199/month
- Annual: $1990/year (save ~17%)
- Setup: $0

Growth Plan:
- Monthly: $499/month
- Annual: $4990/year (save ~17%)
- Setup: $0

Enterprise Plan:
- Monthly: $999/month
- Annual: $9990/year (save ~17%)
- Setup: $500

Add-ons (each with monthly/annual + setup fees):
- AI Analytics: $99/mo, $990/yr, $299 setup
- AI Websites: $49/mo, $490/yr, $199 setup
- Custom Apps: $99/mo, $990/yr, $499 setup
- BI Dashboards: $99/mo, $990/yr, $299 setup
- Text Alerts: $29/mo, $290/yr, $0 setup
```

### 3. PayPal Configuration

1. **Get PayPal Credentials:**
   - Go to https://developer.paypal.com
   - Create a live app for production
   - Get Client ID and Client Secret

2. **Create Products and Plans:**
   - Use PayPal's API or dashboard to create products
   - Create subscription plans for each billing cycle
   - Update `.env.prod` with actual Plan IDs

3. **Set up Webhooks:**
   - Configure webhook endpoint: `https://yourdomain.com/api/checkout/webhook/paypal`
   - Subscribe to these events:
     - `BILLING.SUBSCRIPTION.ACTIVATED`
     - `BILLING.SUBSCRIPTION.CANCELLED`
     - `BILLING.SUBSCRIPTION.SUSPENDED`
     - `PAYMENT.SALE.COMPLETED`
     - `BILLING.SUBSCRIPTION.PAYMENT.FAILED`

### 4. Update Environment Variables

Update your `.env.prod` file with real values:

```bash
# Stripe - Replace with actual price IDs
STRIPE_STARTER_MONTHLY_PRICE_ID=price_your_actual_price_id
STRIPE_STARTER_ANNUAL_PRICE_ID=price_your_actual_price_id
# ... (all other price IDs)

# PayPal - Replace with actual credentials and plan IDs
PAYPAL_CLIENT_ID=your_actual_client_id
PAYPAL_CLIENT_SECRET=your_actual_client_secret
PAYPAL_WEBHOOK_ID=your_actual_webhook_id
PAYPAL_STARTER_MONTHLY_PLAN_ID=P-your_actual_plan_id
# ... (all other plan IDs)
```

### 5. Update Frontend UI

The checkout pages need to be updated to support payment provider selection. You'll need to:

1. **Add payment method selection UI**
2. **Update checkout forms** to include payment provider choice
3. **Handle different redirect flows** for Stripe vs PayPal

Example UI addition:
```html
<div class="payment-methods">
    <label>
        <input type="radio" name="payment_provider" value="stripe" checked>
        <span>Credit/Debit Card (Stripe)</span>
    </label>
    <label>
        <input type="radio" name="payment_provider" value="paypal">
        <span>PayPal</span>
    </label>
</div>
```

### 6. Update API Routes

Replace your current checkout routes with the enhanced ones:

1. **Backup current checkout.py**
2. **Rename `checkout_enhanced.py` to `checkout.py`**
3. **Update imports** in your main application

### 7. Testing

Test both payment flows:

**Stripe Testing:**
- Use test card: `4242 4242 4242 4242`
- Any future expiry date
- Any CVC

**PayPal Testing:**
- Use PayPal sandbox environment
- Test with PayPal sandbox accounts

### 8. Webhook Endpoints

Update your webhook URLs:

**Stripe:**
- Endpoint: `https://yourdomain.com/api/checkout/webhook/stripe`
- Events: `checkout.session.completed`, `invoice.payment_succeeded`, `invoice.payment_failed`

**PayPal:**
- Endpoint: `https://yourdomain.com/api/checkout/webhook/paypal`

## Database Schema Overview

### New Tables Created:

1. **customers** - Customer information and payment provider IDs
2. **products** - All your plans and add-ons with pricing
3. **subscriptions** - Active subscriptions with provider links
4. **subscription_items** - Individual items in a subscription
5. **payments** - All payment transactions and attempts
6. **payment_methods** - Saved payment methods per customer
7. **invoices** - Generated invoices for accounting
8. **invoice_items** - Line items on invoices
9. **webhook_events** - Audit log of all webhook events
10. **payment_audit_logs** - Full audit trail for compliance

## Key Benefits

✅ **Scalable Architecture** - Supports multiple payment providers
✅ **ERP-Ready** - Full accounting and audit capabilities
✅ **Customer Choice** - Users can pay via Stripe or PayPal
✅ **Comprehensive Tracking** - Every transaction is logged
✅ **Webhook Security** - Verified webhook processing
✅ **Future-Proof** - Easy to add more payment providers

## Support

If you encounter issues:

1. **Check logs** in `webhook_events` table for failed webhooks
2. **Verify credentials** in `.env.prod`
3. **Test webhooks** using provider dashboard tools
4. **Check payment statuses** in the `payments` table

## Next Development Phase

After setup is complete, you can work on:
- Customer portal for subscription management
- Billing history and invoice downloads
- Usage-based billing features
- Advanced reporting dashboard
- Mobile app payment integration