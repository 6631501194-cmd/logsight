from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    timestamp: datetime | None = Field(default=None, validation_alias="@timestamp")
    source: str = "api"
    event_type: str = "unknown"
    event_subtype: str | None = None
    severity: int | None = Field(default=None, ge=0, le=10)
    action: str | None = None
    vendor: str | None = None
    product: str | None = None
    ip: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    src_port: int | None = Field(default=None, ge=0, le=65535)
    dst_port: int | None = Field(default=None, ge=0, le=65535)
    protocol: str | None = None
    user: str | None = None
    host: str | None = None
    process: str | None = None
    url: str | None = None
    http_method: str | None = None
    status_code: int | None = None
    rule_name: str | None = None
    rule_id: str | None = None
    cloud: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list, validation_alias="_tags")
    raw: dict[str, Any] | None = None


class IngestResponse(BaseModel):
    id: str
    tenant: str
    source: str
    timestamp: datetime
