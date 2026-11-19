from typing import Protocol

from error_digest.core.models import LogEntry


class Source(Protocol):
    def fetch_errors(self, since: str) -> list[LogEntry]: ...
