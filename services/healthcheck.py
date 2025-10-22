import json
import socket
import sys
from pathlib import Path
from typing import Callable, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.publer_client import ping as publer_ping

LOGS = Path("logs")
LOGS.mkdir(parents=True, exist_ok=True)
OUT = LOGS / "health_last.json"


def check_publer() -> Dict[str, str | bool]:
    ok = publer_ping()
    return {"name": "publer", "ok": ok, "detail": "pong" if ok else "fail"}


def check_dns(host: str = "app.xseller.ai") -> Dict[str, str | bool]:
    try:
        ip = socket.gethostbyname(host)
        return {"name": "dns_app", "ok": True, "detail": ip}
    except Exception as exc:  # noqa: BLE001
        return {"name": "dns_app", "ok": False, "detail": str(exc)}


def run_all() -> Dict[str, bool | List[Dict[str, str | bool]]]:
    checks: List[Callable[[], Dict[str, str | bool]]] = [check_publer, check_dns]
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
