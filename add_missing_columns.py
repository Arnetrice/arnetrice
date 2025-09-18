"""
Add Missing Columns to Client Submissions Table
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.prod')

def add_missing_columns():
    """Add missing columns to client_submissions table"""

    print("Adding Missing Columns...")
    print("=" * 30)

    # Database connection
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5433')
    db_user = os.getenv('DB_USERNAME', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME', 'katurah_db')

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)

        # Columns to add (one by one with separate transactions)
        columns_to_add = [
            ('payment_frequency', 'VARCHAR(20)'),
            ('accept_policies', 'BOOLEAN DEFAULT false'),
            ('save_card', 'BOOLEAN DEFAULT false'),
            ('updated_at', 'TIMESTAMP'),
            ('stripe_subscription_id', 'VARCHAR(255)'),
            ('setup_fee_amount', 'NUMERIC DEFAULT 0'),
            ('subscription_status', 'VARCHAR(50) DEFAULT \'inactive\''),
            ('subscription_start_date', 'TIMESTAMP'),
            ('subscription_end_date', 'TIMESTAMP'),
            ('next_billing_date', 'TIMESTAMP')
        ]

        for col_name, col_definition in columns_to_add:
            session = Session()
            try:
                # Check if column exists
                result = session.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'client_submissions' AND column_name = :col_name
                """), {"col_name": col_name}).fetchone()

                if result:
                    print(f"[EXISTS] {col_name}")
                else:
                    # Add the column
                    session.execute(text(f"""
                        ALTER TABLE client_submissions
                        ADD COLUMN {col_name} {col_definition}
                    """))
                    session.commit()
                    print(f"[ADDED] {col_name} ({col_definition})")

            except Exception as e:
                print(f"[ERROR] Failed to add {col_name}: {str(e)}")
                session.rollback()
            finally:
                session.close()

        print("\n[SUCCESS] Column addition complete!")

    except Exception as e:
        print(f"[ERROR] Database connection failed: {str(e)}")

if __name__ == "__main__":
    add_missing_columns()