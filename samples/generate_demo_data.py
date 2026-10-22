#!/usr/bin/env python3
"""Create idempotent tenant-scoped demonstration events through LogSight's HTTP API."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value)


def request(url: str, method: str, payload: dict | None = None, headers: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    request_headers = {"Accept": "application/json", **(headers or {})}
    if body:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"API request failed with HTTP {error.code}") from error


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def event(seed_id: str, timestamp: datetime, **fields: object) -> dict:
    return {"seed_id": seed_id, "@timestamp": iso(timestamp), "tags": ["demo-data", "phase-3"], **fields}


def demo_a_events(now: datetime) -> list[dict]:
    base = now - timedelta(minutes=30)
    events: list[dict] = []
    for index in range(6):
        events.append(event(f"logsight-demoA-{index + 1:03}", base + timedelta(minutes=index), source="api", event_type="app_login_success", user=f"analyst{index % 3 + 1}@demoa.local", ip=f"10.20.1.{20 + index}", severity=2, action="login", host="portal-a"))
    for index in range(5):
        events.append(event(f"logsight-demoA-{index + 7:03}", base + timedelta(minutes=index + 7), source="api", event_type="app_login_failed", user="admin@demoa.local", ip="203.0.113.77", severity=7, action="deny", host="portal-a", reason="invalid_password"))
    for index in range(5):
        events.append(event(f"logsight-demoA-{index + 12:03}", base + timedelta(minutes=index + 13), source="firewall", vendor="demo", product="ngfw", event_type="firewall_connection", action="deny" if index % 2 else "allow", src_ip=f"198.51.100.{10 + index}", dst_ip="10.20.10.15", src_port=42000 + index, dst_port=443, protocol="tcp", severity=5 if index % 2 else 2, rule_name="External-Web-Policy"))
    for index in range(4):
        events.append(event(f"logsight-demoA-{index + 17:03}", base + timedelta(minutes=index + 19), source="system", event_type="system_warning", host="app-a-01", severity=4, action="alert", process="worker-service", message=["Disk usage above 80%", "Queue processing delay", "Certificate expires soon", "High memory utilization"][index]))
    return events


def demo_b_events(now: datetime) -> list[dict]:
    base = now - timedelta(minutes=24)
    events: list[dict] = []
    for index in range(4):
        events.append(event(f"logsight-demoB-{index + 1:03}", base + timedelta(minutes=index), source="api", event_type="app_login_success", user=f"operator{index + 1}@demob.local", ip=f"10.30.1.{30 + index}", severity=2, action="login", host="portal-b"))
    for index in range(3):
        events.append(event(f"logsight-demoB-{index + 5:03}", base + timedelta(minutes=index + 5), source="api", event_type="app_login_failed", user="viewer@demob.local", ip=f"203.0.113.{130 + index}", severity=4, action="deny", host="portal-b", reason="invalid_password"))
    for index in range(3):
        events.append(event(f"logsight-demoB-{index + 8:03}", base + timedelta(minutes=index + 10), source="firewall", vendor="demo", product="ngfw", event_type="firewall_connection", action="allow", src_ip=f"198.51.100.{50 + index}", dst_ip="10.30.10.20", src_port=44000 + index, dst_port=53, protocol="udp", severity=2, rule_name="DNS-Resolution"))
    for index in range(2):
        events.append(event(f"logsight-demoB-{index + 11:03}", base + timedelta(minutes=index + 15), source="system", event_type="system_warning", host="batch-b-01", severity=3, action="alert", process="scheduler", message=["Backup completed with warnings", "Worker restarted after timeout"][index]))
    return events


def generate(tenant_label: str, events: list[dict], api_url: str) -> tuple[int, int]:
    prefix = "DEMO_A" if tenant_label == "demoA" else "DEMO_B"
    email, password, key = (os.environ[f"{prefix}_{name}"] for name in ("ADMIN_EMAIL", "ADMIN_PASSWORD", "INGESTION_KEY"))
    session = request(f"{api_url}/api/auth/login", "POST", {"email": email, "password": password})
    auth_header = {"Authorization": f"Bearer {session['access_token']}"}
    created = skipped = 0
    for payload in events:
        query = urllib.parse.urlencode({"keyword": payload["seed_id"], "page_size": 1})
        existing = request(f"{api_url}/api/logs?{query}", "GET", headers=auth_header)
        if existing["total"]:
            skipped += 1
            continue
        request(f"{api_url}/ingest", "POST", payload, {"X-Ingestion-Key": key})
        created += 1
    return created, skipped


def main() -> int:
    load_env()
    api_url = os.environ.get("LOGSIGHT_API_URL", "http://localhost:8000").rstrip("/")
    now = datetime.now(UTC)
    for label, events in (("demoA", demo_a_events(now)), ("demoB", demo_b_events(now))):
        created, skipped = generate(label, events, api_url)
        print(f"{label}: created={created}, skipped_existing={skipped}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, KeyError) as error:
        print(f"Sample generation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
