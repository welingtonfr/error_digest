from datetime import timedelta

import pytest

from error_digest.utils.parsers import parse_duration


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("45s", timedelta(seconds=45)),
        ("30m", timedelta(minutes=30)),
        ("24h", timedelta(hours=24)),
        ("48h", timedelta(hours=48)),
        ("1d", timedelta(days=1)),
        ("1h30m", timedelta(hours=1, minutes=30)),
        ("1d2h3m4s", timedelta(days=1, hours=2, minutes=3, seconds=4)),
        ("2d12h", timedelta(days=2, hours=12)),
        ("0s", timedelta(0)),
        ("  1h  ", timedelta(hours=1)),
    ],
)
def test_parse_duration_valid(text, expected):
    assert parse_duration(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "abc",
        "10",
        "h",
        "1x",
        "1.5h",
        "-1h",
        "1h 30m",
        "30m1h",
        "1H",
    ],
)
def test_parse_duration_invalid(text):
    with pytest.raises(ValueError, match="Invalid duration"):
        parse_duration(text)
