import re
from datetime import timedelta


def parse_duration(s: str) -> timedelta:
    """Convert '24h', '30m', '45s', '1d' or combinations '1h30m' in timedelta."""
    pattern = r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    m = re.fullmatch(pattern, s.strip())
    if not m or s.strip() == "":
        raise ValueError(f"Invalid duration: {s!r}")
    d, h, mi, sec = (int(x) if x else 0 for x in m.groups())
    return timedelta(days=d, hours=h, minutes=mi, seconds=sec)
