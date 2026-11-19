import os
import re
from dataclasses import dataclass, field

import yaml
from dotenv import load_dotenv

from error_digest.sinks.github_sink import GithubSink
from error_digest.sinks.sink import Sink
from error_digest.sources.loki_source import LokiSource
from error_digest.sources.source import Source
from error_digest.traces.tempo_trace import TempoTrace
from error_digest.traces.trace import Trace


@dataclass
class Config:
    source: Source
    sinks: list[Sink]
    window: str = "24h"
    max_issues: int = 10
    traces: Trace | None = None
    ignore_rules: list[str] = field(default_factory=list)
    # scrub_rules: list[str] = []

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


def build_traces(traces) -> Trace | None:
    if not traces:
        return None

    match traces["type"]:
        case "tempo":
            return TempoTrace(
                url=traces["connection"]["url"],
                grafana_key=traces["connection"]["grafana_key"],
                datasource_uid=traces["connection"]["datasource_uid"],
            )
        case _:
            raise RuntimeError(f"Unknown traces type: {traces['type']}")


def build_ignore_rules(rules: list[str] | None) -> list[str]:
    rules = rules or []

    for rule in rules:
        if rule.startswith("re:"):
            try:
                re.compile(rule.removeprefix("re:"))
            except re.error as error:
                raise ValueError(f"Invalid ignore regex {rule!r}: {error}") from error

    return rules


def build_sinks(raw_sinks: list | None) -> list[Sink]:
    sinks: list[Sink] = []

    for raw in raw_sinks or []:
        match raw["type"]:
            case "github":
                sinks.append(GithubSink(repo=raw["repo"], token=raw["pat_token"]))
            case _:
                raise RuntimeError(f"Unknown sink type: {raw['type']}")

    return sinks


_ENV_VAR = re.compile(r"\$\{(\w+)\}")


def _expand_env(text: str) -> str:
    def replace(match: re.Match) -> str:
        name = match.group(1)
        value = os.environ.get(name)
        if not value:
            raise RuntimeError(f"Environment variable {name} is not set")
        return value

    return _ENV_VAR.sub(replace, text)


def load_config(path: str) -> Config:
    load_dotenv()

    with open(path) as yaml_opened:
        raw = yaml.safe_load(_expand_env(yaml_opened.read()))

        return Config(
            window=raw["window"],
            max_issues=raw["max_issues"],
            ignore_rules=build_ignore_rules(raw.get("ignore")),
            source=build_source(raw["source"]),
            sinks=build_sinks(raw["sinks"]),
            traces=build_traces(raw.get("traces")),
        )
