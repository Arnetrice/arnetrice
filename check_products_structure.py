"""
Check Products Table Structure
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.prod')

def check_products_structure():
    """Check the actual structure of the products table"""

    print("Checking Products Table Structure...")
    print("=" * 40)

    # Database connection
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5433')
    db_user = os.getenv('DB_USERNAME', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'katurah_db')

    if not db_password:
        print("[ERROR] DB_PASSWORD not found in environment")
        return

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Get table structure
        print("Products table columns:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position;
        """)).fetchall()

        for row in result:
            column_name, data_type, is_nullable, default = row
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"  {column_name}: {data_type} {nullable}{default_str}")

        # Check existing products
        print(f"\nExisting products:")
        result = session.execute(text("SELECT sku, name, base_price, setup_fee FROM products ORDER BY sku")).fetchall()

        for row in result:
            sku, name, base_price, setup_fee = row
            print(f"  {sku}: {name} (${base_price}, setup: ${setup_fee})")

        session.close()

    except Exception as e:
        print(f"[ERROR] Database operation failed: {str(e)}")

if __name__ == "__main__":
    check_products_structure()