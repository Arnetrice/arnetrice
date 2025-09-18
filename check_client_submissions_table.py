"""
Check and Fix Client Submissions Table Structure
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.prod')

def check_and_fix_client_submissions():
    """Check and fix the client_submissions table structure"""

    print("Checking Client Submissions Table...")
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

        # Check if table exists
        table_exists = session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'client_submissions'
            );
        """)).fetchone()[0]

        if not table_exists:
            print("[ERROR] client_submissions table does not exist!")
            return

        # Get current table structure
        print("Current client_submissions table columns:")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'client_submissions'
            ORDER BY ordinal_position;
        """)).fetchall()

        existing_columns = []
        for row in result:
            column_name, data_type, is_nullable, default = row
            existing_columns.append(column_name)
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            default_str = f" DEFAULT {default}" if default else ""
            print(f"  {column_name}: {data_type} {nullable}{default_str}")

        # Check for missing phone column
        if 'phone' not in existing_columns:
            print(f"\n[MISSING] phone column not found. Adding it...")
            try:
                session.execute(text("""
                    ALTER TABLE client_submissions
                    ADD COLUMN phone VARCHAR(25);
                """))
                session.commit()
                print("[SUCCESS] phone column added!")
            except Exception as e:
                print(f"[ERROR] Failed to add phone column: {str(e)}")
                session.rollback()
        else:
            print(f"\n[OK] phone column exists")

        # Check for any other required columns that might be missing
        required_columns = {
            'name': 'VARCHAR(100)',
            'email': 'VARCHAR(255)',
            'phone': 'VARCHAR(25)',
            'company': 'VARCHAR(100)',
            'plan': 'VARCHAR(50)',
            'payment_frequency': 'VARCHAR(20)',
            'add_ons': 'TEXT',
            'accept_policies': 'BOOLEAN',
            'save_card': 'BOOLEAN',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }

        missing_columns = []
        for col_name, col_type in required_columns.items():
            if col_name not in existing_columns:
                missing_columns.append((col_name, col_type))

        if missing_columns:
            print(f"\nAdding {len(missing_columns)} missing columns...")
            for col_name, col_type in missing_columns:
                try:
                    session.execute(text(f"""
                        ALTER TABLE client_submissions
                        ADD COLUMN {col_name} {col_type};
                    """))
                    print(f"[ADDED] {col_name} ({col_type})")
                except Exception as e:
                    print(f"[ERROR] Failed to add {col_name}: {str(e)}")

            session.commit()
            print("[SUCCESS] Missing columns added!")

        # Show final structure
        print(f"\nFinal table structure:")
        result = session.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'client_submissions'
            ORDER BY ordinal_position;
        """)).fetchall()

        for row in result:
            column_name, data_type = row
            print(f"  {column_name}: {data_type}")

        session.close()

    except Exception as e:
        print(f"[ERROR] Database operation failed: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    success = check_and_fix_client_submissions()
    if success:
        print("\n[SUCCESS] Client submissions table check complete!")
    else:
        print("\n[FAILED] Client submissions table check failed!")