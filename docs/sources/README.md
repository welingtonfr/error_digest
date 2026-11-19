# Sources

A source defines where errors are read from. Each source has its own folder with the full reference.

| Type | Description | Docs |
|---|---|---|
| `loki` | Grafana Loki, through the Grafana proxy | [loki/](loki/README.md) |

To add a new source, implement the `Source` protocol (`src/error_digest/sources/source.py`), register it in `build_source` (`src/error_digest/config.py`) and document it in a new folder here.
