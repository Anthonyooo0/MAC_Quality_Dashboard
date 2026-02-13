"""
One-time script to generate an MSAL token cache for GitHub Actions.

Run this locally:
    python get_token_cache.py

It will:
1. Open a device-flow login (same as the dashboard)
2. Print out the serialized token cache
3. You paste that value into the MSAL_TOKEN_CACHE GitHub Actions secret

The cached refresh token auto-renews every time the cron job runs,
so it stays valid indefinitely as long as the job runs at least once
every 90 days.
"""
import os
import sys
import json

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

from msal import PublicClientApplication, SerializableTokenCache

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")

if not TENANT_ID or not CLIENT_ID:
    print("ERROR: Set TENANT_ID and CLIENT_ID in your .env file first.")
    sys.exit(1)

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Mail.Read", "User.Read"]

cache = SerializableTokenCache()
app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

print("Starting device flow login...")
print()

flow = app.initiate_device_flow(scopes=SCOPES)
if "user_code" not in flow:
    print(f"ERROR: {flow.get('error_description', 'Unknown error')}")
    sys.exit(1)

print(f"Go to: https://microsoft.com/devicelogin")
print(f"Enter code: {flow['user_code']}")
print()
print("Waiting for you to complete sign-in...")

result = app.acquire_token_by_device_flow(flow)

if "access_token" not in result:
    print(f"ERROR: {result.get('error_description', 'Login failed')}")
    sys.exit(1)

print()
print("Login successful!")
print()

# Serialize the token cache
cache_json = cache.serialize()

print("=" * 60)
print("COPY EVERYTHING BELOW THIS LINE (it's one long line):")
print("=" * 60)
print(cache_json)
print("=" * 60)
print()
print("Now go to GitHub > Settings > Secrets > Actions")
print("Create a new secret named: MSAL_TOKEN_CACHE")
print("Paste the value above as the secret value.")
