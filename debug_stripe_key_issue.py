"""
Debug Stripe Key Loading Issue
Check how the environment variables are being loaded and used
"""
import os
from dotenv import load_dotenv

def debug_stripe_key_issue():
    """Debug why Stripe key shows as sk_test_*2345 when live key is in .env.prod"""

    print("Debugging Stripe Key Loading...")
    print("=" * 50)

    # Test 1: Check current environment without loading .env
    print("1. Current environment (before loading .env):")
    current_stripe_key = os.getenv('STRIPE_SECRET_KEY')
    print(f"   STRIPE_SECRET_KEY: {current_stripe_key}")

    # Test 2: Load .env.prod explicitly
    print("\n2. Loading .env.prod explicitly:")
    load_dotenv('.env.prod', override=True)
    after_load_key = os.getenv('STRIPE_SECRET_KEY')
    if after_load_key:
        masked_key = after_load_key[:15] + '...' + after_load_key[-4:]
        print(f"   STRIPE_SECRET_KEY: {masked_key}")
        print(f"   Key type: {'live' if after_load_key.startswith('sk_live_') else 'test' if after_load_key.startswith('sk_test_') else 'unknown'}")
        print(f"   Key length: {len(after_load_key)}")
    else:
        print("   STRIPE_SECRET_KEY: Not found")

    # Test 3: Check other environment files
    print("\n3. Checking for other .env files:")
    env_files = ['.env', '.env.local', '.env.development', '.env.test']
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   [EXISTS] {env_file}")
            # Check if it has STRIPE_SECRET_KEY
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'STRIPE_SECRET_KEY' in content:
                        lines = [line for line in content.split('\n') if 'STRIPE_SECRET_KEY' in line and not line.strip().startswith('#')]
                        for line in lines:
                            if '=' in line:
                                key_part = line.split('=', 1)[1].strip()
                                if key_part:
                                    masked = key_part[:15] + '...' + key_part[-4:] if len(key_part) > 20 else key_part
                                    print(f"     Contains: STRIPE_SECRET_KEY={masked}")
            except Exception as e:
                print(f"     Error reading: {e}")
        else:
            print(f"   [MISSING] {env_file}")

    # Test 4: Check FastAPI app configuration
    print("\n4. How does your FastAPI app load the environment?")
    print("   Check these files for environment loading:")

    config_files = [
        'backend/app/config.py',
        'backend/app/settings.py',
        'backend/app/main.py',
        'backend/app/__init__.py'
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   [EXISTS] {config_file}")
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'load_dotenv' in content or 'STRIPE_SECRET_KEY' in content:
                        print(f"     Contains environment loading code")
                        # Show relevant lines
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'load_dotenv' in line or 'STRIPE_SECRET_KEY' in line:
                                print(f"     Line {i+1}: {line.strip()}")
            except Exception as e:
                print(f"     Error reading: {e}")

    # Test 5: Direct Stripe import test
    print("\n5. Testing Stripe import and key usage:")
    try:
        import stripe
        stripe.api_key = after_load_key

        # Try a simple Stripe API call
        print(f"   Stripe library version: {stripe.__version__}")
        print(f"   API key set: {stripe.api_key[:15]}...{stripe.api_key[-4:] if stripe.api_key else 'None'}")

        # Test API call
        customers = stripe.Customer.list(limit=1)
        print(f"   [SUCCESS] Stripe API call successful")

    except stripe.error.AuthenticationError as e:
        print(f"   [AUTH ERROR] {str(e)}")
    except Exception as e:
        print(f"   [ERROR] {str(e)}")

    print("\n" + "=" * 50)
    print("[NEXT STEPS]")
    print("1. Check if your FastAPI app is loading a different .env file")
    print("2. Restart your FastAPI server after environment changes")
    print("3. Verify the Stripe key in your dashboard is active")
    print("4. Check if there are multiple environment files overriding each other")

if __name__ == "__main__":
    debug_stripe_key_issue()