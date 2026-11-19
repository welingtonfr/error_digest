from unittest.mock import MagicMock, patch

from error_digest.config import build_sinks
from error_digest.core.issue import build_issue
from error_digest.core.models import Group, LogEntry
from error_digest.sinks.github_sink import GithubSink


def _sink():
    return GithubSink(repo="org/app", token="t")


def test_write_creates_issue_and_returns_number():
    resp = MagicMock()
    resp.json.return_value = {"number": 42}
    with patch(
        "error_digest.sinks.github_sink.requests.post", return_value=resp
    ) as post:
        assert _sink().write("T", "B", ["bug"]) == "42"
    assert post.call_args.args[0] == "https://api.github.com/repos/org/app/issues"
    assert post.call_args.kwargs["json"] == {
        "title": "T",
        "body": "B",
        "labels": ["bug"],
    }
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer t"
    resp.raise_for_status.assert_called_once()


def test_comment_posts_to_issue():
    with patch("error_digest.sinks.github_sink.requests.post") as post:
        _sink().comment("42", "again")
    assert post.call_args.args[0].endswith("/repos/org/app/issues/42/comments")
    assert post.call_args.kwargs["json"] == {"body": "again"}


def test_build_sinks_github_and_unknown():
    sinks = build_sinks([{"type": "github", "repo": "o/r", "pat_token": "x"}])
    assert isinstance(sinks[0], GithubSink) and sinks[0].token == "x"
    assert build_sinks(None) == []


def test_build_issue_includes_counts_and_trace():
    entry = LogEntry(message="boom", timestamp=1_700_000_000_000_000_000)
    group = Group(
        fingerprint="abc",
        sample="boom",
        count=3,
        first_seen=entry.timestamp,
        last_seen=entry.timestamp,
        entries=[entry],
        trace="trace: 1 spans",
    )
    title, body, labels = build_issue(group)
    assert title and "boom" in body and "**Occurrences:** 3" in body
    assert "trace: 1 spans" in body and labels == ["error-digest"]
