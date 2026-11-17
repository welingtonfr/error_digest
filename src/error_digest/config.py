from dataclasses import dataclass

import yaml

from error_digest.sinks.sink import Sink
from error_digest.sources.loki_source import LokiSource
from error_digest.sources.source import Source


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
                datasource_uid=source["connection"]["datasource_uid"],
                labels=source.get("labels", {}),
            )
        case _:
            raise RuntimeError


def build_sinks(rawSinks: list) -> list[Sink]:
    sinks: list[Sink] = []

    return sinks


def load_config(path: str) -> Config:
    with open(path) as yaml_opened:
        raw = yaml.safe_load(yaml_opened)

        return Config(
            window=raw["window"],
            max_issues=raw["max_issues"],
            source=build_source(raw["source"]),
            sinks=build_sinks(raw["sinks"]),
        )
