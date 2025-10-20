import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


def normalize_cname_target(target: str) -> str:
    """Ensure the CNAME target is a hostname as required by GoDaddy."""
    parsed_target = urlparse(target)
    if parsed_target.scheme:
        if not parsed_target.hostname:
            raise SystemExit("❌ CNAME_TARGET URL is invalid; missing hostname.")
        return parsed_target.hostname.rstrip(".")
    return target.rstrip("/")


def main() -> None:
    # Load GoDaddy credentials and CNAME details from .env
    load_dotenv()
    api_key = os.getenv("GODADDY_API_KEY")
    api_secret = os.getenv("GODADDY_API_SECRET")
    domain = os.getenv("GODADDY_DOMAIN")
    cname_name = os.getenv("CNAME_NAME", "app")
    cname_target = os.getenv("CNAME_TARGET")
    shopper_id = os.getenv("GODADDY_SHOPPER_ID")

    if not all([api_key, api_secret, domain, cname_target]):
        raise SystemExit("❌ Missing one or more required environment variables.")

    cname_target = normalize_cname_target(cname_target)

    headers = {
        "Authorization": f"sso-key {api_key}:{api_secret}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if shopper_id:
        headers["X-Shopper-Id"] = shopper_id

    payload = [
        {
            "type": "CNAME",
            "name": cname_name,
            "data": cname_target,
            "ttl": 3600,
        }
    ]

    url = f"https://api.godaddy.com/v1/domains/{domain}/records/CNAME/{cname_name}"
    print(f"➡️ Updating DNS record for {cname_name}.{domain} → {cname_target}")
    resp = requests.put(url, headers=headers, json=payload, timeout=10)

    if resp.status_code in (200, 201, 204):
        print("✅ CNAME record created/updated successfully.")
        return

    try:
        error_payload = resp.json()
    except ValueError:
        error_payload = resp.text

    if resp.status_code == 403:
        guidance = (
            "GoDaddy returned ACCESS_DENIED. Verify that the API key/secret belong to the "
            "account that owns the domain. If the key is associated with a reseller or "
            "delegated account, supply GODADDY_SHOPPER_ID in .env."
        )
        print(f"❌ Error 403: {error_payload}\n{guidance}")
    else:
        print(f"❌ Error {resp.status_code}: {error_payload}")


if __name__ == "__main__":
    main()
