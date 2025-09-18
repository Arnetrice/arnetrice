"""
Database Migration Script for Payment System Tables
Run this script to create all necessary payment-related tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from backend.app.config import settings
from backend.app.models_payment import Base, PaymentProvider, PaymentStatus, SubscriptionStatus, InvoiceStatus

def create_payment_tables():
    """Create all payment-related database tables"""
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables defined in models_payment.py
    Base.metadata.create_all(bind=engine)

    print("Payment tables created successfully:")
    print("- customers")
    print("- products")
    print("- subscriptions")
    print("- subscription_items")
    print("- payments")
    print("- payment_methods")
    print("- invoices")
    print("- invoice_items")
    print("- webhook_events")
    print("- payment_audit_logs")

def seed_products(engine):
    """Seed initial products data"""
    from sqlalchemy.orm import Session
    from backend.app.models_payment import Product
    import os

    session = Session(engine)

    # Define products with their Stripe and PayPal IDs
    products = [
        # Hosting Plans
        {
            "sku": "HOSTING_STARTER",
            "name": "Starter Hosting Plan",
            "description": "Perfect for small businesses starting their digital journey",
            "category": "hosting",
            "base_price": 199.00,
            "setup_fee": 0,
            "is_subscription": True,
            "is_addon": False,
            "stripe_product_id": os.getenv("STRIPE_STARTER_MONTHLY"),
            "stripe_price_id_monthly": None,  # These need to be created in Stripe
            "stripe_price_id_annual": None,
            "paypal_plan_id": os.getenv("PAYPAL_STARTER_MONTHLY_PLAN_ID")
        },
        {
            "sku": "HOSTING_GROWTH",
            "name": "Growth Hosting Plan",
            "description": "For businesses ready to scale with advanced features",
            "category": "hosting",
            "base_price": 499.00,
            "setup_fee": 0,
            "is_subscription": True,
            "is_addon": False,
            "stripe_product_id": os.getenv("STRIPE_GROWTH_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "paypal_plan_id": os.getenv("PAYPAL_GROWTH_MONTHLY_PLAN_ID")
        },
        {
            "sku": "HOSTING_ENTERPRISE",
            "name": "Enterprise Hosting Plan",
            "description": "Custom solutions for large organizations",
            "category": "hosting",
            "base_price": 999.00,
            "setup_fee": 500,
            "is_subscription": True,
            "is_addon": False,
            "stripe_product_id": os.getenv("STRIPE_ENTERPRISE_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "paypal_plan_id": os.getenv("PAYPAL_ENTERPRISE_MONTHLY_PLAN_ID")
        },

        # Add-ons
        {
            "sku": "ADDON_AI_ANALYTICS",
            "name": "Advanced AI Analytics",
            "description": "AI-powered insights and predictive analytics",
            "category": "addon",
            "base_price": 99.00,
            "setup_fee": 299,
            "is_subscription": True,
            "is_addon": True,
            "stripe_product_id": os.getenv("STRIPE_ADVANCED_AI_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "stripe_setup_price_id": None,
            "paypal_plan_id": os.getenv("PAYPAL_ADVANCED_AI_PRODUCT_ID")
        },
        {
            "sku": "ADDON_AI_WEBSITES",
            "name": "AI Powered Websites",
            "description": "Intelligent website features with AI integration",
            "category": "addon",
            "base_price": 49.00,
            "setup_fee": 199,
            "is_subscription": True,
            "is_addon": True,
            "stripe_product_id": os.getenv("STRIPE_AI_WEBSITES_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "stripe_setup_price_id": os.getenv("STRIPE_AI_WEBSITES_SETUP"),
            "paypal_plan_id": os.getenv("PAYPAL_AI_WEBSITES_PRODUCT_ID")
        },
        {
            "sku": "ADDON_CUSTOM_APPS",
            "name": "Custom Applications",
            "description": "Tailored application development for your needs",
            "category": "addon",
            "base_price": 99.00,
            "setup_fee": 499,
            "is_subscription": True,
            "is_addon": True,
            "stripe_product_id": os.getenv("STRIPE_CUSTOM_APPS_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "stripe_setup_price_id": os.getenv("STRIPE_CUSTOM_APPS_SETUP"),
            "paypal_plan_id": os.getenv("PAYPAL_CUSTOM_APPS_PRODUCT_ID")
        },
        {
            "sku": "ADDON_TEXT_ALERTS",
            "name": "Text Alerts",
            "description": "SMS notifications and alerts for critical events",
            "category": "addon",
            "base_price": 29.00,
            "setup_fee": 0,
            "is_subscription": True,
            "is_addon": True,
            "stripe_product_id": os.getenv("STRIPE_TEXT_ALERTS_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "paypal_plan_id": os.getenv("PAYPAL_TEXT_ALERTS_PRODUCT_ID")
        },
        {
            "sku": "ADDON_BI_DASHBOARDS",
            "name": "Specialized BI Dashboards",
            "description": "Custom business intelligence dashboards",
            "category": "addon",
            "base_price": 99.00,
            "setup_fee": 299,
            "is_subscription": True,
            "is_addon": True,
            "stripe_product_id": os.getenv("STRIPE_BI_DASHBOARDS_MONTHLY"),
            "stripe_price_id_monthly": None,
            "stripe_price_id_annual": None,
            "stripe_setup_price_id": os.getenv("STRIPE_BI_DASHBOARDS_SETUP"),
            "paypal_plan_id": None
        }
    ]

    # Add products to database
    for product_data in products:
        existing = session.query(Product).filter_by(sku=product_data["sku"]).first()
        if not existing:
            product = Product(**product_data)
            session.add(product)
            print(f"Added product: {product_data['name']}")
        else:
            print(f"Product already exists: {product_data['name']}")

    session.commit()
    session.close()

def migrate():
    """Run the complete migration"""
    try:
        engine = create_engine(settings.DATABASE_URL)

        # Create tables
        create_payment_tables()

        # Seed initial data
        seed_products(engine)

        print("\nMigration completed successfully!")
        print("Next steps:")
        print("1. Create Stripe price IDs for each product/plan")
        print("2. Create PayPal subscription plans")
        print("3. Update .env.prod with the correct price/plan IDs")
        print("4. Test payment flows")

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()