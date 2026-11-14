from typing import Protocol


class Sink(Protocol):
    def write(self, title: str, body: str, labels: list[str]): ...
