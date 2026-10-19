from datetime import UTC

from app.schemas import IngestRequest
from app.services.normalization import normalize_log


def test_normalizer_preserves_raw_and_maps_ip():
    event = IngestRequest.model_validate({"source": "API", "event_type": "login_failed", "ip": "203.0.113.7", "@timestamp": "2026-10-19T00:00:00Z", "extra": "preserved"})
    normalized = normalize_log(event)
    assert normalized["source"] == "api"
    assert normalized["src_ip"] == "203.0.113.7"
    assert normalized["timestamp"].tzinfo == UTC
    assert normalized["raw"]["extra"] == "preserved"
