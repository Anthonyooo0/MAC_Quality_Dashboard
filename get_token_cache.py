"""
One-time login tool for MAC Quality Dashboard.
Signs into Microsoft and saves a token file for GitHub Actions.
"""
import os
import sys
import webbrowser

from msal import PublicClientApplication, SerializableTokenCache

# Hardcoded - same values as in .env
TENANT_ID = "422e0e56-e8fe-4fc5-8554-b9b89f3cadac"
CLIENT_ID = "4d218a58-d028-4fa3-a0dc-8c8df56fb413"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Mail.Read", "User.Read"]

def main():
    print("=" * 50)
    print("  MAC Quality Dashboard - Microsoft Login")
    print("=" * 50)
    print()

    cache = SerializableTokenCache()
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        print(f"ERROR: {flow.get('error_description', 'Unknown error')}")
        input("Press Enter to close...")
        sys.exit(1)

    code = flow["user_code"]
    print(f"Your login code is:  {code}")
    print()
    print("A browser window will open. If it doesn't, go to:")
    print("  https://microsoft.com/devicelogin")
    print()
    print(f"Enter the code:  {code}")
    print()

    # Try to open the browser automatically
    try:
        webbrowser.open("https://microsoft.com/devicelogin")
    except Exception:
        pass

    print("Waiting for you to sign in...")
    print()

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        print(f"ERROR: {result.get('error_description', 'Login failed')}")
        print()
        input("Press Enter to close...")
        sys.exit(1)

    print("Login successful!")
    print()

    # Save token cache to a file
    cache_json = cache.serialize()
    output_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "msal_token_cache.txt")
    with open(output_path, "w") as f:
        f.write(cache_json)

    print(f"Token saved to: {output_path}")
    print()
    print("Send the file 'msal_token_cache.txt' to Anthony.")
    print("He will add it to the GitHub Actions secrets.")
    print()
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
