import json
import os
import sys
import urllib.request

url = os.getenv("LOGSIGHT_INGEST_URL", "http://localhost:8000/ingest")
key = os.environ["LOGSIGHT_INGESTION_KEY"]
with open(sys.argv[1] if len(sys.argv) > 1 else "samples/api-login-failed.json", encoding="utf-8") as file:
    request = urllib.request.Request(url, data=file.read().encode(), method="POST", headers={"Content-Type": "application/json", "X-Ingestion-Key": key})
    print(urllib.request.urlopen(request).read().decode())
