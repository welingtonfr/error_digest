from datetime import UTC, datetime

import requests
from pydantic import BaseModel

from error_digest.core.models import LogEntry
from error_digest.utils.parsers import parse_duration


class LokiSource(BaseModel):
    url: str
    grafana_key: str
    datasource_uid: str
    labels: dict[str, str]
    limit: int = 1000
    timeout: int = 30

    def fetch_errors(self, since: str) -> list[LogEntry]:
        streams = self._get_grafana_logs(since)

        entries: list[LogEntry] = []
        for stream in streams:
            labels = stream.get("stream", {})
            for ts, line in stream.get("values", []):
                entries.append(
                    LogEntry(
                        message=line,
                        timestamp=int(ts),
                        trace_id=labels.get("trace_id") or None,
                        span_id=labels.get("span_id") or None,
                        labels=labels,
                    )
                )

        entries.sort(key=lambda entry: entry.timestamp)
        return entries

    def _get_grafana_logs(self, since: str):
        now = datetime.now(UTC)

        since_deltatime = parse_duration(since)

        start = int((now - since_deltatime).timestamp() * 1e9)
        end = int(now.timestamp() * 1e9)

        params = {
            "query": (
                f"{self._get_grafana_query()}"
                ' | detected_level=~"(?i)(error|critical|fatal)"'
            ),
            "start": start,
            "end": end,
            "limit": self.limit,
            "direction": "backward",
        }

        path = (
            f"/api/datasources/proxy/uid/{self.datasource_uid}/loki/api/v1/query_range"
        )

        resp = requests.get(
            f"{self.url}{path}",
            params=params,
            headers={"Authorization": f"Bearer {self.grafana_key}"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["data"]["result"]

    def _get_grafana_query(self):
        selector = ", ".join(f'{k}="{self._escape(v)}"' for k, v in self.labels.items())

        return "{" + selector + "}"

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')
