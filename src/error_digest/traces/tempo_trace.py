import requests
from pydantic import BaseModel

from error_digest.traces.summary import summarize_trace_otlp


class TempoTrace(BaseModel):
    url: str
    grafana_key: str
    datasource_uid: str
    timeout: int = 30

    def get(self, trace_id: str) -> str | None:
        path = f"/api/datasources/proxy/uid/{self.datasource_uid}/api/traces/{trace_id}"

        resp = requests.get(
            f"{self.url}{path}",
            headers={"Authorization": f"Bearer {self.grafana_key}"},
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return summarize_trace_otlp(resp.text)
