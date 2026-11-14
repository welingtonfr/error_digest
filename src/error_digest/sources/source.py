from datetime import timedelta
from typing import Protocol

class Source(Protocol):
    def fetch_errors(self, since: timedelta) -> list[str]: ...
