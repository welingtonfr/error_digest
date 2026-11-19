import re

from error_digest.config import Config
from error_digest.core.models import LogEntry


def _matches(rule: str, message: str) -> bool:
    if rule.startswith("re:"):
        regex = rule.removeprefix("re:")

        founded = re.search(regex, message, re.IGNORECASE)

        return founded is not None

    return rule.casefold() in message.casefold()


def filter_log_entries(config: Config, logs: list[LogEntry]) -> list[LogEntry]:
    """Drop entries whose message matches any ignore rule."""
    rules = [rule for rule in config.ignore_rules if rule]

    if not rules:
        return logs

    return [
        log for log in logs if not any(_matches(rule, log.message) for rule in rules)
    ]
