import os
import requests
from dotenv import load_dotenv

# Load GoDaddy credentials and CNAME details from .env
load_dotenv()
API_KEY = os.getenv("GODADDY_API_KEY")
API_SECRET = os.getenv("GODADDY_API_SECRET")
DOMAIN = os.getenv("GODADDY_DOMAIN")
CNAME_NAME = os.getenv("CNAME_NAME", "app")
CNAME_TARGET = os.getenv("CNAME_TARGET")

if not all([API_KEY, API_SECRET, DOMAIN, CNAME_TARGET]):
    raise SystemExit("❌ Missing one or more required environment variables.")

headers = {
    "Authorization": f"sso-key {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
}

payload = [
    {
        "type": "CNAME",
        "name": CNAME_NAME,
        "data": CNAME_TARGET,
        "ttl": 3600,
    }
]

url = f"https://api.godaddy.com/v1/domains/{DOMAIN}/records/CNAME/{CNAME_NAME}"

print(f"➡️ Updating DNS record for {CNAME_NAME}.{DOMAIN} → {CNAME_TARGET}")
resp = requests.put(url, headers=headers, json=payload, timeout=10)
if resp.status_code in (200, 201, 204):
    print("✅ CNAME record created/updated successfully.")
else:
    print("❌ Error:", resp.status_code, resp.text)
