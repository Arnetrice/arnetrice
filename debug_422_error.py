"""
Debug 422 Validation Error
Identify which field is causing the validation failure
"""
import requests
import json

def debug_422_error():
    """Test different field combinations to identify validation issues"""

    print("Debugging 422 Validation Error...")
    print("=" * 50)

    # Base valid data
    base_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "555-123-4567",
        "plan": "starter",
        "billing_cycle": "monthly",
        "payment_provider": "stripe",
        "accept_policies": True
    }

    # Test cases to identify the problem field
    test_cases = [
        {
            "name": "Minimal required fields only",
            "data": base_data.copy()
        },
        {
            "name": "With company field",
            "data": {**base_data, "company": "Test Company"}
        },
        {
            "name": "With empty add_ons",
            "data": {**base_data, "add_ons": []}
        },
        {
            "name": "With save_card",
            "data": {**base_data, "save_card": False}
        },
        {
            "name": "With billing_info",
            "data": {**base_data,
                    "billing_info": {
                        "card_number": "4242424242424242",
                        "expiry_date": "12/25",
                        "cvv": "123",
                        "address": "123 Test St",
                        "city": "Test City",
                        "state": "CA",
                        "zip": "12345",
                        "country": "US"
                    }}
        },
        {
            "name": "Complete data with all fields",
            "data": {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "555-123-4567",
                "company": "Test Company",
                "plan": "starter",
                "billing_cycle": "monthly",
                "payment_provider": "stripe",
                "add_ons": [],
                "billing_info": {
                    "card_number": "4242424242424242",
                    "expiry_date": "12/25",
                    "cvv": "123",
                    "address": "123 Test St",
                    "city": "Test City",
                    "state": "CA",
                    "zip": "12345",
                    "country": "US"
                },
                "save_card": False,
                "accept_policies": True
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Fields included: {list(test_case['data'].keys())}")

        try:
            response = requests.post(
                'http://localhost:8000/api/checkout/create-session',
                headers={'Content-Type': 'application/json'},
                json=test_case['data'],
                timeout=10
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 422:
                # Validation error - show details
                error_detail = response.json()
                print(f"   [VALIDATION ERROR]")

                if 'detail' in error_detail:
                    if isinstance(error_detail['detail'], list):
                        for error in error_detail['detail']:
                            field = '.'.join(str(x) for x in error.get('loc', []))
                            msg = error.get('msg', '')
                            error_type = error.get('type', '')
                            print(f"     - Field: {field}")
                            print(f"       Error: {msg}")
                            print(f"       Type: {error_type}")
                    else:
                        print(f"     {error_detail['detail']}")

            elif response.status_code == 200:
                result = response.json()
                print(f"   [SUCCESS] Response: success={result.get('success', False)}")
                if result.get('error'):
                    print(f"   Error message: {result['error']}")

        except requests.exceptions.ConnectionError:
            print("   [ERROR] Connection failed - is the server running?")
        except Exception as e:
            print(f"   [ERROR] {str(e)}")

    print("\n" + "=" * 50)
    print("Debugging Complete!")

    # Also test what the frontend is actually sending
    print("\n[FRONTEND DATA FORMAT]")
    print("The frontend checkout forms typically send data like this:")
    frontend_format = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "(555) 123-4567",
        "company": "Acme Corp",
        "plan": "starter",
        "payment_frequency": "monthly",  # Note: frontend might use this instead of billing_cycle
        "payment_provider": "stripe",
        "add_ons": ["advanced_ai_analytics"],  # Array of addon IDs
        "billing_info": {
            "card_number": "4242 4242 4242 4242",  # With spaces
            "expiry_date": "12/25",
            "cvv": "123",
            "address": "123 Main St",
            "address2": "",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102",
            "country": "US"
        },
        "save_card": True,  # Boolean
        "accept_policies": True  # Boolean
    }
    print(json.dumps(frontend_format, indent=2))

if __name__ == "__main__":
    debug_422_error()