

from datetime import timedelta
from error_digest.sources.source import Source
from pydantic import BaseModel


class LokiSource(BaseModel):
    url: str
    grafana_key: str
    datasource_uid: str

    def fetch_errors(self, since: timedelta) -> list[str]:
        return []
