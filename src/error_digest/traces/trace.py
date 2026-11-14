from typing import Protocol


class Trace(Protocol):
    def get(self, trace_id: str) -> str: ...
