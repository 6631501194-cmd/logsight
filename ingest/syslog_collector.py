"""Working UDP Syslog collector: preserves a datagram and forwards it through the tenant-scoped HTTP ingest API."""
import json
import os
import socket
import urllib.request
from datetime import UTC, datetime

endpoint = os.environ["SYSLOG_INGEST_URL"]
api_key = os.environ["SYSLOG_INGESTION_KEY"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5514))
print("Listening for UDP syslog on 5514", flush=True)

while True:
    data, address = sock.recvfrom(65535)
    message = data.decode("utf-8", errors="replace")
    payload = {
        "source": "firewall",
        "event_type": "syslog",
        "ip": address[0],
        "@timestamp": datetime.now(UTC).isoformat(),
        "raw": {"message": message, "sender_ip": address[0], "sender_port": address[1]},
    }
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), method="POST", headers={"Content-Type": "application/json", "X-Ingestion-Key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print(f"Forwarded syslog: {response.status}", flush=True)
    except Exception as exc:
        print(f"Failed to forward syslog: {exc}", flush=True)
