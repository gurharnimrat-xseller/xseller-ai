import json
import os
import socket
from pathlib import Path
from typing import Callable, Dict, List

import requests

LOGS = Path("logs")
LOGS.mkdir(parents=True, exist_ok=True)
OUT = LOGS / "health_last.json"


def check_repurpose(api_key: str | None = None) -> Dict[str, str | bool]:
    key = api_key or os.getenv("REPURPOSE_API_KEY")
    if not key:
        return {"name": "repurpose", "ok": False, "detail": "missing_key"}
    try:
        response = requests.get(
            "https://api.repurpose.io/v1/platforms",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        ok = response.status_code == 200
        detail = f"status={response.status_code}"
    except Exception as exc:  # noqa: BLE001
        ok = False
        detail = str(exc)
    return {"name": "repurpose", "ok": ok, "detail": detail}


def check_snapchat_repurpose() -> Dict[str, str | bool]:
    key = os.getenv("REPURPOSE_API_KEY")
    if not key:
        return {"name": "snapchat_repurpose", "ok": False, "detail": "missing_key"}
    try:
        response = requests.get(
            "https://api.repurpose.io/v1/platforms",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        ok = response.status_code == 200 and "snapchat" in response.text.lower()
        detail = f"status={response.status_code}"
    except Exception as exc:  # noqa: BLE001
        ok = False
        detail = str(exc)
    return {"name": "snapchat_repurpose", "ok": ok, "detail": detail}


def check_dns(host: str = "app.xseller.ai") -> Dict[str, str | bool]:
    try:
        ip = socket.gethostbyname(host)
        return {"name": "dns_app", "ok": True, "detail": ip}
    except Exception as exc:  # noqa: BLE001
        return {"name": "dns_app", "ok": False, "detail": str(exc)}


def run_all() -> Dict[str, bool | List[Dict[str, str | bool]]]:
    checks: List[Callable[[], Dict[str, str | bool]]] = [
        check_repurpose,
        check_snapchat_repurpose,
        check_dns,
    ]
    results = {"ok": True, "checks": []}
    for check in checks:
        result = check()
        results["checks"].append(result)
        if not result["ok"]:
            results["ok"] = False
    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2))
