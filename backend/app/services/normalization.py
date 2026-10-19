from datetime import UTC, datetime
from typing import Any

from app.schemas import IngestRequest


def normalize_log(payload: IngestRequest) -> dict[str, Any]:
    """Convert an accepted source payload into the persistent common event schema."""
    raw = payload.raw if payload.raw is not None else payload.model_dump(by_alias=True, mode="json")
    timestamp = payload.timestamp or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return {
        "timestamp": timestamp,
        "source": payload.source.lower().strip(),
        "vendor": payload.vendor,
        "product": payload.product,
        "event_type": payload.event_type,
        "event_subtype": payload.event_subtype,
        "severity": payload.severity,
        "action": payload.action,
        "src_ip": payload.src_ip or payload.ip,
        "dst_ip": payload.dst_ip,
        "src_port": payload.src_port,
        "dst_port": payload.dst_port,
        "protocol": payload.protocol,
        "user_name": payload.user,
        "host": payload.host,
        "process": payload.process,
        "url": payload.url,
        "http_method": payload.http_method,
        "status_code": payload.status_code,
        "rule_name": payload.rule_name,
        "rule_id": payload.rule_id,
        "cloud": payload.cloud,
        "raw": raw,
        "tags": payload.tags,
    }
