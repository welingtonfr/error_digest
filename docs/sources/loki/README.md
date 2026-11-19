# Source: Loki

Reads logs from Loki **through the Grafana proxy** (`/api/datasources/proxy/uid/<uid>/loki/api/v1/query_range`).

## Configuration

```yaml
source:
  type: loki
  labels:
    service_name: api
    deployment_environment: production
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_LOKI_UID}
    grafana_key: ${GRAFANA_KEY}
```

| Key | Required | Description |
|---|---|---|
| `labels` | no | `label: value` pairs that form the Loki selector. Quotes and backslashes in values are escaped. |
| `connection.url` | yes | Grafana URL. |
| `connection.datasource_uid` | yes | UID of the Loki datasource. |
| `connection.grafana_key` | yes | Token sent as `Authorization: Bearer`. |

Environment variables used by this source: `GRAFANA_URL`, `GRAFANA_KEY`, `GRAFANA_LOKI_UID` (see [General settings](../../configuration.md#1-general-settings)).

## How the query is built

With the labels above, the query sent to Loki is:

```logql
{service_name="api", deployment_environment="production"} | detected_level=~"(?i)(error|critical|fatal)"
```

- Only logs whose `detected_level` is `error`, `critical` or `fatal` are returned (case-insensitive).
- The search runs from newest to oldest (`direction=backward`) and returns **at most 1000 lines**, with a 30s timeout. Both values exist in the code (`limit`, `timeout`) but are **not yet configurable from the YAML**.
- The result becomes a list of entries with message, timestamp, `trace_id` and `span_id` (read from the stream labels) and the remaining labels.

## Tips

- **A wrong label returns an empty result, without an error.** Check the names in Grafana → Explore → Label browser. A selector with a label that does not exist (e.g. `job`) simply matches nothing.
- **Messages do not need to contain the word "error".** The filter is on the log level, not on the text.
- If there are more than 1000 errors in the window, the oldest ones are left out.
- `401 Unauthorized` means the token is invalid, revoked or expired.

## Limitation: direct connection

Only the path through Grafana is implemented today. Connecting directly to Loki (without Grafana) is not supported yet.
