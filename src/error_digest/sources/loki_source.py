

from datetime import UTC, datetime, timedelta, timezone
from error_digest.utils.parsers import parse_duration
import requests
from pydantic import BaseModel
import json

class LokiSource(BaseModel):
    url: str
    grafana_key: str
    datasource_uid: str
    labels: dict[str, str]

    def fetch_errors(self, since: str) -> list[str]:
        response = self._get_grafana_logs(since);

        response

        return []

    def _get_grafana_logs(self, since: str):
        now = datetime.now(UTC)

        since_deltatime = parse_duration(since)

        start = int((now - since_deltatime).timestamp() * 1e9)
        end = int(now.timestamp() * 1e9)

        query = self._get_grafana_query()

        params = {
            "query": f'sum(rate({query}[{since}])) by (level)',
              "start": start,
              "end": end,
              "step": "30s",
        }

        path = f"/api/datasources/proxy/uid/{self.datasource_uid}/loki/api/v1/query_range"

        resp = requests.get(
            f"{self.url}{path}",
                params=params,
                headers={"Authorization": f"Bearer {self.grafana_key}"},
            )
        resp.raise_for_status()
        return resp.json()['data']['result']

    def _get_grafana_query(self):
        selector = ", ".join(f'{k}="{v}"' for k, v in self.labels.items())

        query = "{" + selector + "}"

        return query
