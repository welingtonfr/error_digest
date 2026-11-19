import hashlib
import re

from error_digest.core.models import Group, LogEntry

_RULES: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            re.IGNORECASE,
        ),
        "<uuid>",
    ),
    (re.compile(r"\b0x[0-9a-f]+\b", re.IGNORECASE), "<hex>"),
    (re.compile(r"\b[0-9a-f]{16,}\b", re.IGNORECASE), "<hex>"),
    (re.compile(r"'[^']*'"), "<str>"),
    (re.compile(r'"[^"]*"'), "<str>"),
    (re.compile(r"\b\d+(?:\.\d+)?\b"), "<n>"),
    (re.compile(r"\s+"), " "),
]


def normalize(message: str) -> str:
    text = message
    for pattern, replacement in _RULES:
        text = pattern.sub(replacement, text)
    return text.strip()


def fingerprint(message: str) -> str:
    return hashlib.sha1(normalize(message).encode()).hexdigest()[:12]


def group_by_fingerprint(entries: list[LogEntry]) -> list[Group]:
    buckets: dict[str, list[LogEntry]] = {}
    for entry in entries:
        buckets.setdefault(fingerprint(entry.message), []).append(entry)

    groups: list[Group] = []
    for fp, items in buckets.items():
        items.sort(key=lambda e: e.timestamp)
        latest_with_trace = next((e for e in reversed(items) if e.trace_id), None)
        groups.append(
            Group(
                fingerprint=fp,
                sample=items[-1].message,
                count=len(items),
                first_seen=items[0].timestamp,
                last_seen=items[-1].timestamp,
                entries=items,
                trace_id=latest_with_trace.trace_id if latest_with_trace else None,
            )
        )

    groups.sort(key=lambda g: g.count, reverse=True)
    return groups
