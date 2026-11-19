from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    message: str
    timestamp: int  # nanoseconds since epoch
    trace_id: str | None = None
    span_id: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class Group(BaseModel):
    fingerprint: str
    sample: str
    count: int
    first_seen: int
    last_seen: int
    entries: list[LogEntry]
    trace_id: str | None = None
    trace: str | None = None
