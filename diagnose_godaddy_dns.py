import os
import requests
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("GODADDY_API_KEY")
API_SECRET = os.getenv("GODADDY_API_SECRET")
DOMAIN = os.getenv("GODADDY_DOMAIN", "xseller.ai")
SHOPPER_ID = os.getenv("GODADDY_SHOPPER_ID", "").strip()

BASE = "https://api.godaddy.com/v1"
headers = {
    "Authorization": f"sso-key {API_KEY}:{API_SECRET}",
    "Accept": "application/json",
    "Content-Type": "application/json",
}
if SHOPPER_ID:
    headers["X-Shopper-Id"] = SHOPPER_ID


def call(method, path, **kw):
    r = requests.request(method, f"{BASE}{path}", headers=headers, timeout=20, **kw)
    print(f"{method} {path} -> {r.status_code}")
    try:
        print(r.json())
    except Exception:
        print(r.text)
    return r


print("1) Checking domain ownership…")
r = call("GET", f"/domains/{DOMAIN}")
if r.status_code != 200:
    print("\n❌ Your key/secret isn’t authorized for this domain. Causes:")
    print("   - Key is not Production")
    print("   - Domain is in a different GoDaddy account")
    print("   - You’re a delegate (UI only), API lacks permission")
    print("   - Add X-Shopper-Id (Customer ID) if still 403 after fixing above")
    raise SystemExit()

print("\n2) Checking if GoDaddy hosts DNS (nameservers & zone)…")
r_ns = call("GET", f"/domains/{DOMAIN}/records/NS")
if r_ns.status_code in (200, 204):
    print("✅ DNS zone appears accessible via GoDaddy API.")
else:
    print("⚠️ Could not read NS records via API; DNS may be hosted elsewhere.")
    print("   If your nameservers are Cloudflare/Route53/etc., GoDaddy API cannot edit your DNS.")
    print("   In that case, add the CNAME in that DNS provider instead.")
