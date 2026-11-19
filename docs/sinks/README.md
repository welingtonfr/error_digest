# Sinks

A sink is where the digest is delivered (an issue tracker, for example).

> **Status:** not implemented yet. The `sinks` list is read from the YAML, but `build_sinks` returns an empty list, so nothing is sent today.

| Type | Status | Docs |
|---|---|---|
| `github` | planned (class skeleton exists) | [github/](github/README.md) |
| `clickup` | planned (class skeleton exists) | [clickup/](clickup/README.md) |

## Contract

Every sink implements the `Sink` protocol (`src/error_digest/sinks/sink.py`):

```python
class Sink(Protocol):
    def write(self, title: str, body: str, labels: list[str]) -> str: ...
    def comment(self, content: str): ...
```

To add a new sink, implement the protocol, register it in `build_sinks` (`src/error_digest/config.py`) and document it in a new folder here.
