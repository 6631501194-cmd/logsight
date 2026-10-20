from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    timestamp: Annotated[datetime | None, Field(validation_alias="@timestamp")] = None
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
    tags: Annotated[list[str], Field(validation_alias="_tags")] = Field(default_factory=list)
    raw: dict[str, Any] | None = None


class IngestResponse(BaseModel):
    id: str
    tenant: str
    source: str
    timestamp: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    tenant: str


class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    timestamp: datetime
    source: str
    event_type: str
    severity: int | None
    src_ip: str | None
    user_name: str | None
    raw: dict[str, Any]


class PageResponse(BaseModel):
    items: list[LogResponse]
    total: int
    page: int
    page_size: int
