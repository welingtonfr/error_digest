# Trace backend: Tempo

The `traces` section is **optional**. When present, each error group fetches the trace of its most recent occurrence that has a `trace_id`.

Fetches the trace through the Grafana proxy (`/api/datasources/proxy/uid/<uid>/api/traces/<trace_id>`).

```yaml
traces:
  type: tempo
  connection:
    url: ${GRAFANA_URL}
    datasource_uid: ${GRAFANA_TEMPO_UID}
    grafana_key: ${GRAFANA_KEY}
```

| Key | Required | Description |
|---|---|---|
| `connection.url` | yes | Grafana URL. |
| `connection.datasource_uid` | yes | UID of the Tempo datasource. |
| `connection.grafana_key` | yes | Token sent as `Authorization: Bearer`. |

## How the trace reaches the digest

Tempo returns the full OTLP JSON, which is huge. Error Digest condenses it into compact text:

```
trace: 2 spans, 1 with error
- +0ms 8ms api GET /x
! +1ms 1ms api SELECT db.statement=select 1 | boom
    exception PDOException: bad column
```

- Spans are in start order, with relative time (`+Nms`) and duration.
- `!` marks spans with an error, followed by the status message and any exceptions.
- Only useful attributes appear (HTTP, database, RPC, messaging), truncated to 200 characters.
- At most 40 spans; error spans are included first and the rest becomes `... N more spans omitted`.
- A trace that is not found (404) results in `None`, without breaking the digest.

## Notes

- This summary understands the **OTLP** format. A backend that returns another format (native Jaeger, Zipkin, Sentry) would need its own class.
- The `trace_id` comes from the log's `trace_id` label. Logs without that label do not get a trace.
- As with Loki, connecting directly to Tempo (without Grafana) is not supported yet.

Environment variables used: `GRAFANA_URL`, `GRAFANA_KEY`, `GRAFANA_TEMPO_UID` (see [General settings](../../configuration.md#1-general-settings)).
