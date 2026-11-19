from error_digest.config import Config
from error_digest.core.enrich import enrich_groups
from error_digest.core.filter import filter_log_entries
from error_digest.core.fingerprint import group_by_fingerprint
from error_digest.core.issue import build_issue
from error_digest.core.models import Group
from error_digest.sinks.sink import Sink


def run_digest(config: Config, dry_run: bool = True):
    log_entries = config.source.fetch_errors(since=config.window)

    log_entries = filter_log_entries(config, log_entries)

    groups = group_by_fingerprint(log_entries)[: config.max_issues]

    groups_enriched = enrich_groups(config, groups)

    if not dry_run:
        for sink in config.sinks:
            _sink_handle_write(groups_enriched, sink)

    return groups_enriched


def _sink_handle_write(groups: list[Group], sink: Sink):
    for group in groups:
        title, body, labels = build_issue(group)
        sink.write(title, body, labels)
