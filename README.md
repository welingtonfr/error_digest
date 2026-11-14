# Error Digest

Turn noisy production logs into a short, actionable list of issues.

Error Digest pulls error logs from your observability stack (currently Grafana Loki), groups similar errors together, ranks them, and files them as issues in your tracker (currently planned: GitHub). It ships as both a **Python library** and a **command-line tool**.

> **Status:** early development (v0.1.0). The architecture and configuration are in place, but the pipeline steps are still being implemented. See [Roadmap](#roadmap).

## How it works

```
Source (Loki) → group by fingerprint → ignore / rank → enrich with traces (Tempo)
              → scrub sensitive data → compare with saved state → Sink (GitHub issues)
```

1. **Collect** errors from a source within a time window (e.g. the last 24h).
2. **Group** similar errors by fingerprint so one bug is one issue, not a thousand log lines.
3. **Filter and rank** — drop ignored patterns and keep the top N.
4. **Enrich** with traces for extra context.
5. **Scrub** sensitive data (e.g. CPF, email) before anything leaves your infrastructure.
6. **Create or update** issues, using local state to avoid duplicates.

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

| Option | Description |
| --- | --- |
| `-c`, `--config` | Path to the YAML config file (default: `error_digest.yaml`) |
| `--dry-run` / `--apply` | Only show results, or create issues (default: `--dry-run`) |

You can also run it as a module: `python -m error_digest run -c config-dev.yaml`.

## Library usage

```python
from error_digest.config import load_config
from error_digest.pipeline import run_digest

cfg = load_config("config-dev.yaml")
run_digest(cfg, dry_run=True)
```

Sources and sinks are small `Protocol`s, so adding your own is straightforward:

```python
class Source(Protocol):
    def fetch_errors(self, since: timedelta) -> list[str]: ...

class Sink(Protocol):
    def write(self, title: str, body: str, labels: list[str]): ...
```

## Configuration

```yaml
window: 24h          # how far back to look
max_issues: 10       # cap on issues per run

source:
  type: loki
  connection:
    url: https://grafana.example.com
    datasource_uid: <loki-datasource-uid>
    grafana_key: <grafana-service-account-token>

traces:
  type: tempo
  url: http://tempo:3200

sinks:
  - type: github
    repo: my-org/my-app
    pat_token: GITHUB_TOKEN     # name of the env var holding the token

ignore:                          # error patterns to skip
  - 'Connection reset by peer'

scrub:                           # sensitive data to redact
  - cpf
  - email

state:
  path: ./digest_state.db        # remembers already-reported errors
```

**Keep secrets out of git.** Don't commit real tokens in config files; load them from environment variables or a `.env` file, and make sure those files are in `.gitignore`.

## Project layout

```
src/error_digest/
├── cli.py          # Typer CLI entry point
├── config.py       # YAML config loading
├── pipeline.py     # The digest pipeline
├── sources/        # Where errors come from (Loki)
├── sinks/          # Where issues go (GitHub)
└── agents/         # Automated fix suggestions (planned)
```

## Roadmap

- [x] CLI skeleton and config loading
- [ ] Loki source: fetch errors
- [ ] Fingerprinting and grouping
- [ ] Ignore rules, ranking, and `max_issues`
- [ ] Tempo trace enrichment
- [ ] Sensitive data scrubbing
- [ ] SQLite state store (deduplicate and update existing issues)
- [ ] GitHub sink
- [ ] Fix-suggestion agent
