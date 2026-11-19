# Configuration

Error Digest is configured with a YAML file (e.g. `config-dev.yaml`) plus environment variables for secrets.

Run with a specific config file:

```bash
python -m error_digest run --config config-dev.yaml
```

Contents:

1. [General settings](#1-general-settings)
2. [Sources](#2-sources)
3. [Traces](#3-traces)
4. [Ignore](#4-ignore)
5. [Sinks](#5-sinks)

Full example:

```yaml
window: 48h
max_issues: 10

source:
  type: loki
  labels:
    service_name: api
    deployment_environment: production
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_LOKI_UID}
    grafana_key: ${GRAFANA_KEY}

traces:
  type: tempo
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_TEMPO_UID}
    grafana_key: ${GRAFANA_KEY}

ignore:
  - 'Connection reset by peer'
  - 're:timeout after \d+ms'
```

---

## 1. General settings

### Top-level keys

| Key | Required | Default | Description |
|---|---|---|---|
| `window` | yes | — | Time window to fetch errors from, counted backwards from now. |
| `max_issues` | yes | — | Maximum number of error groups kept in the digest, most frequent first. |
| `source` | yes | — | Where the logs come from. See [Sources](#2-sources). |
| `traces` | no | no traces | Trace backend used to enrich each group. See [Traces](#3-traces). |
| `ignore` | no | `[]` | Errors to drop before grouping. See [Ignore](#4-ignore). |
| `sinks` | yes | — | Where the digest goes. The list is read today, but **no sink is implemented yet**. See [Sinks](#5-sinks). |

### `window` format

Accepts `d`, `h`, `m` and `s`, lowercase, in descending order and without spaces.

| Valid | Invalid |
|---|---|
| `45s`, `30m`, `24h`, `1d` | `1H` (uppercase) |
| `1h30m`, `1d2h3m4s` | `30m1h` (wrong order) |
| `0s` | `1h 30m` (space), `1.5h` (decimal), `-1h`, `10` (no unit) |

An invalid value raises `ValueError: Invalid duration`.

### Environment variables (`${VAR}`)

Any YAML value can use `${NAME}`. The program reads the `.env` file in the project root (via `python-dotenv`) and then replaces each `${NAME}` with its value.

- A variable that is **unset or empty** stops the program with `Environment variable NAME is not set`.
- Variables already set in the shell **take precedence** over `.env`.
- Keep secrets in `.env`, never in the YAML. Both `.env` and `config-dev.yaml` are in `.gitignore`.

Use `.env.example` as a template:

| Variable | Purpose |
|---|---|
| `GRAFANA_URL` | Grafana base URL. |
| `GRAFANA_KEY` | Grafana service account token. The **Viewer** role is enough, since everything is read-only. |
| `GRAFANA_LOKI_UID` | UID of the Loki datasource in Grafana. |
| `GRAFANA_TEMPO_UID` | UID of the Tempo datasource in Grafana. |

> If you get `401 Unauthorized`, the token is invalid, revoked or expired. Generate a new one and make sure there are no quotes or trailing spaces in `.env`.

---

## 2. Sources

The source defines where errors are read from. Each source has its own folder with the full reference: see [docs/sources](sources/README.md).

| Type | Docs |
|---|---|
| `loki` | [sources/loki](sources/loki/README.md) |

```yaml
source:
  type: loki
  labels:
    service_name: api
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_LOKI_UID}
    grafana_key: ${GRAFANA_KEY}
```

---

## 3. Traces

The `traces` section is **optional**. Each trace backend has its own folder with the full reference: see [docs/traces](traces/README.md).

| Type | Docs |
|---|---|
| `tempo` | [traces/tempo](traces/tempo/README.md) |

```yaml
traces:
  type: tempo
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_TEMPO_UID}
    grafana_key: ${GRAFANA_KEY}
```

---

## 4. Ignore

Rules to drop errors before grouping, as plain text or regex (`re:` prefix). Full reference: [docs/ignore](ignore/README.md).

```yaml
ignore:
  - 'Connection reset by peer'
  - 're:timeout after \d+ms'
```

## 5. Sinks

Where the digest is delivered. **Not implemented yet.** See [docs/sinks](sinks/README.md).
