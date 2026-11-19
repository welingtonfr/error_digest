from datetime import UTC, datetime

from error_digest.core.models import Group

TITLE_MAX = 120
LABELS = ["error-digest"]


def build_title(group: Group) -> str:
    sample = " ".join(group.sample.split())
    title = f"[{group.fingerprint}] {sample}"
    if len(title) > TITLE_MAX:
        title = title[: TITLE_MAX - 3] + "..."
    return title


def _format_time(timestamp_ns: int) -> str:
    return datetime.fromtimestamp(timestamp_ns / 1e9, UTC).strftime(
        "%Y-%m-%d %H:%M UTC"
    )


def build_body(group: Group) -> str:
    parts = [
        f"**Occurrences:** {group.count}",
        f"**First seen:** {_format_time(group.first_seen)}",
        f"**Last seen:** {_format_time(group.last_seen)}",
        f"**Fingerprint:** `{group.fingerprint}`",
        "",
        "### Sample message",
        "```",
        group.sample,
        "```",
    ]

    if group.trace:
        parts += ["", "### Trace", "```", group.trace, "```"]

    return "\n".join(parts)


def build_issue(group: Group) -> tuple[str, str, list[str]]:
    return build_title(group), build_body(group), list(LABELS)
