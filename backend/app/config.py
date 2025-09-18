import os
from dotenv import load_dotenv

load_dotenv('.env.prod')

class Settings:
    # Database Configuration
    # Support both single DATABASE_URL and separate variables
    def get_database_url(self):
        # If DATABASE_URL is provided, use it
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
        
        # Otherwise, build from separate variables
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_username = os.getenv("DB_USERNAME", "postgres")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_name = os.getenv("DB_NAME", "arnetrice_db")
        
        return f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @property
    def DATABASE_URL(self):
        return self.get_database_url()
    
    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    
    # Stripe settings
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_STARTER_PRICE_ID = os.getenv("STRIPE_STARTER_PRICE_ID", "")
    STRIPE_GROWTH_PRICE_ID = os.getenv("STRIPE_GROWTH_PRICE_ID", "")
    
    # App settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
    
    # CORS settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://arnetrice.com",
        "https://www.arnetrice.com"
    ]

settings = Settings()
