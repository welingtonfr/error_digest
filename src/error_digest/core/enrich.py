from error_digest.config import Config
from error_digest.core.models import Group


def enrich_groups(config: Config, groups: list[Group]) -> list[Group]:
    for group in groups:
        if config.traces and group.trace_id:
            group.trace = config.traces.get(group.trace_id)

    return groups
