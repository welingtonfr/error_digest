# Traces

A trace backend enriches each error group with the trace of its most recent occurrence. The section is **optional**: without `traces`, the digest contains only the grouped logs.

| Type | Description | Docs |
|---|---|---|
| `tempo` | Grafana Tempo, through the Grafana proxy | [tempo/](tempo/README.md) |

To add a new backend, implement the `Trace` protocol (`src/error_digest/traces/trace.py`), register it in `build_traces` (`src/error_digest/config.py`) and document it in a new folder here. Backends that do not return OTLP need their own summarizer.
