"""
Check and Populate Missing Products in ERP Tables
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.prod')

def check_and_populate_products():
    """Check for missing products and populate them"""

    print("Checking ERP Products...")
    print("=" * 40)

    # Database connection - construct from individual components
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5433')
    db_user = os.getenv('DB_USERNAME', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'katurah_db')

    if not db_password:
        print("[ERROR] DB_PASSWORD not found in environment")
        return

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(f"Connecting to database: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Check if products table exists and has data
        result = session.execute(text("SELECT COUNT(*) FROM products")).fetchone()
        product_count = result[0] if result else 0

        print(f"Current products in database: {product_count}")

        # Check for specific hosting plan products
        hosting_products = [
            ('HOSTING_STARTER', 'Starter Hosting Plan', 199.00, 299.00),
            ('HOSTING_GROWTH', 'Growth Hosting Plan', 499.00, 499.00),
            ('HOSTING_ENTERPRISE', 'Enterprise Hosting Plan', 1299.00, 999.00)
        ]

        print("\nChecking for hosting plan products:")
        missing_products = []

        for sku, name, price, setup_fee in hosting_products:
            result = session.execute(
                text("SELECT id FROM products WHERE sku = :sku"),
                {"sku": sku}
            ).fetchone()

            if result:
                print(f"   [OK] {name} ({sku}) exists")
            else:
                print(f"   [MISSING] {name} ({sku})")
                missing_products.append((sku, name, price, setup_fee))

        # Insert missing products
        if missing_products:
            print(f"\nInserting {len(missing_products)} missing products...")

            for sku, name, price, setup_fee in missing_products:
                try:
                    session.execute(text("""
                        INSERT INTO products (sku, name, description, base_price, setup_fee, product_type, is_active, created_at, updated_at)
                        VALUES (:sku, :name, :description, :base_price, :setup_fee, 'hosting', true, NOW(), NOW())
                    """), {
                        "sku": sku,
                        "name": name,
                        "description": f"{name} - Professional hosting and analytics solution",
                        "base_price": price,
                        "setup_fee": setup_fee
                    })
                    print(f"   [INSERTED] {name}")
                except Exception as e:
                    print(f"   [ERROR] Failed to insert {name}: {str(e)}")

            session.commit()
            print("\nProducts insertion complete!")
        else:
            print("\nAll hosting products are present!")

        # Check add-on products
        print("\nChecking for add-on products:")
        addon_products = [
            ('ADDON_AI_ANALYTICS', 'Advanced AI Analytics', 99.00, 0.00),
            ('ADDON_BI_DASHBOARDS', 'Specialized BI Dashboards', 99.00, 1000.00),
            ('ADDON_AI_WEBSITES', 'AI Powered Websites', 49.00, 1500.00),
            ('ADDON_CUSTOM_APPS', 'Custom Applications', 99.00, 2000.00),
            ('ADDON_TEXT_ALERTS', 'Text Alerts', 49.00, 0.00)
        ]

        missing_addons = []
        for sku, name, price, setup_fee in addon_products:
            result = session.execute(
                text("SELECT id FROM products WHERE sku = :sku"),
                {"sku": sku}
            ).fetchone()

            if result:
                print(f"   [OK] {name} ({sku}) exists")
            else:
                print(f"   [MISSING] {name} ({sku})")
                missing_addons.append((sku, name, price, setup_fee))

        # Insert missing add-ons
        if missing_addons:
            print(f"\nInserting {len(missing_addons)} missing add-on products...")

            for sku, name, price, setup_fee in missing_addons:
                try:
                    session.execute(text("""
                        INSERT INTO products (sku, name, description, base_price, setup_fee, product_type, is_active, created_at, updated_at)
                        VALUES (:sku, :name, :description, :base_price, :setup_fee, 'addon', true, NOW(), NOW())
                    """), {
                        "sku": sku,
                        "name": name,
                        "description": f"{name} - Premium add-on service",
                        "base_price": price,
                        "setup_fee": setup_fee
                    })
                    print(f"   [INSERTED] {name}")
                except Exception as e:
                    print(f"   [ERROR] Failed to insert {name}: {str(e)}")

            session.commit()
            print("\nAdd-on products insertion complete!")
        else:
            print("\nAll add-on products are present!")

        # Final count
        result = session.execute(text("SELECT COUNT(*) FROM products")).fetchone()
        final_count = result[0] if result else 0
        print(f"\nFinal product count: {final_count}")

        session.close()

    except Exception as e:
        print(f"[ERROR] Database operation failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = check_and_populate_products()
    if success:
        print("\n[SUCCESS] Product check and population complete!")
    else:
        print("\n[FAILED] Product check failed!")