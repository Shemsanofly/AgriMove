#!/usr/bin/env python
"""Check if Africa's Talking sandbox credentials in .env are valid."""
from sms_service import _ENV_FILE, verify_at_credentials, _load_at_credentials


def main():
    username, api_key, _ = _load_at_credentials()
    print("Env file:", _ENV_FILE)
    print("Username:", username)
    print("Key loaded:", bool(api_key))
    print("Key length:", len(api_key) if api_key else 0)
    print("Starts with atsk_:", api_key.startswith("atsk_") if api_key else False)

    ok, msg = verify_at_credentials()
    print("Valid:", ok)
    print("Detail:", msg)

    if not ok:
        print()
        print("Fix:")
        print("  1. Open https://account.africastalking.com/apps/sandbox")
        print("  2. Click Settings -> API Key -> Generate (enter your password)")
        print("  3. Copy the ENTIRE key (starts with atsk_)")
        print("  4. Paste in .env: AT_API_KEY=atsk_...")
        print("  5. Restart: python app.py")


if __name__ == "__main__":
    main()
