from typing import Protocol


class Sink(Protocol):
    def write(self, title: str, body: str, labels: list[str]) -> str:
        """Create an issue and return its id."""
        ...

    def comment(self, issue_id: str, content: str) -> None:
        """Add a comment to an existing issue."""
        ...
