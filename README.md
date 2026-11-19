# Error Digest

Turn noisy production logs into a short, actionable list of issues, and let an **agent propose the fix**.

Error Digest pulls error logs from your observability stack (currently Grafana Loki), groups similar errors together, ranks them, and files them as issues in your tracker (currently planned: GitHub). It ships as both a **Python library** and a **command-line tool**.

## The fix agent

Finding the error is half of the work. The goal of Error Digest is to go one step further: for each grouped error, an **agent** receives the context already collected (sample message, how often it happens, and the trace summary) and **suggests a correction**, so the issue arrives with a proposed fix instead of just a stack of logs.

> **Planned.** The agent is not implemented yet (`src/error_digest/agents/` is still empty). Today the pipeline stops at the grouped, enriched errors.

> **Status:** early development (v0.1.0). Working today: Loki source, fingerprint grouping, ignore rules and Tempo trace enrichment. Not implemented yet: sinks (GitHub, ClickUp), `scrub`, `state` and the fix agent.

## How it works

```
Source (Loki) → group by fingerprint → ignore / rank → enrich with traces (Tempo)
              → scrub sensitive data → compare with saved state
              → fix agent (suggest a correction) → Sink (GitHub issues)
```

1. **Collect** errors from a source within a time window (e.g. the last 24h).
2. **Group** similar errors by fingerprint so one bug is one issue, not a thousand log lines.
3. **Filter and rank** — drop ignored patterns and keep the top N.
4. **Enrich** with traces for extra context.
5. **Scrub** sensitive data (e.g. CPF, email) before anything leaves your infrastructure.
6. **Suggest a fix** — an agent analyzes each group and its trace and proposes a correction.
7. **Create or update** issues, with the suggested fix attached, using local state to avoid duplicates.

## Installation

Requires Python 3.11+.

```bash
pip install -e .
```

## CLI usage

```bash
# Preview what would be reported (default, creates nothing)
error-digest run --config config-dev.yaml

# Actually create issues
error-digest run --config config-dev.yaml --apply
```

| Option                  | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| `-c`, `--config`        | Path to the YAML config file (default: `error_digest.yaml`) |
| `--dry-run` / `--apply` | Only show results, or create issues (default: `--dry-run`)  |

You can also run it as a module: `python -m error_digest run -c config-dev.yaml`.

## Library usage

`Config` is a plain dataclass, so you can load it from a YAML file **or** build it in code.

From a file:

```python
from error_digest.config import load_config
from error_digest.pipeline import run_digest

cfg = load_config("config-dev.yaml")
groups = run_digest(cfg, dry_run=True)
```

Or by hand, without any YAML:

```python
from error_digest.config import Config
from error_digest.pipeline import run_digest
from error_digest.sources.loki_source import LokiSource
from error_digest.traces.tempo_trace import TempoTrace

cfg = Config(
    window="24h",
    max_issues=10,
    source=LokiSource(
        url="https://grafana.example.com",
        grafana_key="<grafana-service-account-token>",
        datasource_uid="<loki-datasource-uid>",
        labels={"service_name": "api"},
    ),
    traces=TempoTrace(
        url="https://grafana.example.com",
        grafana_key="<grafana-service-account-token>",
        datasource_uid="<tempo-datasource-uid>",
    ),
    sinks=[],
    ignore_rules=["Connection reset by peer", r"re:timeout after \d+ms"],
)

groups = run_digest(cfg)
```

`run_digest` returns the error groups (fingerprint, sample message, count, first/last seen and, when `traces` is set, the trace summary).

`${VAR}` expansion, `.env` loading and the validation of `re:` rules happen in `load_config` only. When building `Config` in code, pass the real values yourself; an invalid regex built by hand fails when the filter runs.

## Extending

Sources, trace backends and sinks are small `Protocol`s, so adding your own is straightforward. Any object with the right methods works, with no inheritance needed:

```python
class Source(Protocol):
    def fetch_errors(self, since: str) -> list[LogEntry]: ...


class Trace(Protocol):
    def get(self, trace_id: str) -> str | None: ...


class Sink(Protocol):
    def write(self, title: str, body: str, labels: list[str]) -> str: ...
    def comment(self, content: str): ...
```

For example, a source that reads from memory:

```python
class MemorySource:
    def fetch_errors(self, since: str) -> list[LogEntry]:
        return [LogEntry(message="boom", timestamp=1)]


cfg = Config(source=MemorySource(), sinks=[], window="24h", max_issues=10)
```

To use a custom class from the YAML as well, register it in `build_source`, `build_traces` or `build_sinks` (`src/error_digest/config.py`).

Full reference in [docs](docs/configuration.md):

- [General settings](docs/configuration.md#1-general-settings): `window`, `max_issues`, environment variables
- [Sources](docs/sources/README.md): one folder per source ([Loki](docs/sources/loki/README.md))
- [Traces](docs/traces/README.md): one folder per backend ([Tempo](docs/traces/tempo/README.md))
- [Ignore](docs/ignore/README.md): text and regex rules
- [Sinks](docs/sinks/README.md): GitHub (ClickUp planned)

`scrub` and `state` (see **Dedup** in the [Roadmap](#roadmap)) are planned but not implemented yet.

**Keep secrets out of git.** Don't commit real tokens in config files; load them from environment variables or a `.env` file (see `.env.example`), and make sure those files are in `.gitignore`.

## Project layout

```
src/error_digest/
├── cli.py          # Typer CLI entry point
├── config.py       # YAML config loading
├── pipeline.py     # The digest pipeline
├── sources/        # Where errors come from (Loki)
├── sinks/          # Where issues go (GitHub)
└── agents/         # Fix agent: suggests a correction for each error (planned)
```

## Roadmap

Done:

- [x] CLI skeleton and config loading (YAML, `${VAR}` and `.env`)
- [x] Loki source (through the Grafana proxy)
- [x] Fingerprint grouping
- [x] Ignore rules (plain text and `re:` regex)
- [x] Tempo trace enrichment, summarized from OTLP
- [x] GitHub sink (creates issues with `--apply`; not tested against the real API yet)

Planned:

- [ ] **Dedup:** avoid duplicate issues. Remember what was already reported (`state` in the config, local SQLite keyed by sink and fingerprint) and, when the same error comes back, add a comment to the existing issue through the sink's `comment` instead of opening a new one. Until this lands, every `--apply` opens new issues for the same errors.
- [ ] **Scrub:** redact sensitive data (e.g. CPF, email) from messages and traces before anything leaves your infrastructure (`scrub` in the config).
- [ ] **Rank:** today groups are ordered by number of occurrences and cut at `max_issues`. Next: score by recency, growth against the previous window and severity, so a new burst ranks above a constant old error.
- [ ] **Fix agent:** an agent that receives each group and its trace summary and suggests a correction, attached to the issue (see [The fix agent](#the-fix-agent)).
- [ ] **More sinks:** ClickUp first (skeleton exists), then others such as Jira, Linear and Slack. Each one implements the `Sink` protocol, see [docs/sinks](docs/sinks/README.md).
- [ ] **More sources and trace backends:** direct connection to Loki and Tempo without Grafana, and other backends (e.g. Jaeger, Sentry).

## License

[MIT](LICENSE)
