from dataclasses import dataclass

import yaml
from pydantic import BaseModel

from error_digest.sinks.sink import Sink
from error_digest.sources.source import Source
from error_digest.sources.loki_source import LokiSource

@dataclass
class Config:
    source: Source
    sinks: list[Sink]
    window: str = "24h"
    max_issues: int = 10
    # ignore_rules: list[str] = []
    # scrub_rules: list[str] = []


    # traces: TraceSource

    # state: StateStore


def build_source(source) -> Source:
    match source["type"]:
        case "loki":
            return LokiSource(
                url=source["connection"]["url"],
                grafana_key=source["connection"]["grafana_key"],
                datasource_uid=source["connection"]["datasource_uid"]
            )
        case _:
            raise RuntimeError


def build_sinks(rawSinks: list) -> list[Sink]:
    sinks: list[Sink] = []

    return sinks


def load_config(path: str) -> Config:
    raw = yaml.safe_load(open(path))

    return Config(
        window=raw["window"],
        max_issues=raw["max_issues"],
        source=build_source(raw["source"]),
        sinks=build_sinks(raw["sinks"])
    )
