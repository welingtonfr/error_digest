import pytest

from error_digest.config import Config, build_ignore_rules
from error_digest.core.filter import filter_log_entries
from error_digest.core.models import LogEntry


class FakeSource:
    def fetch_errors(self, since: str) -> list[LogEntry]:
        return []


def _config(rules):
    return Config(source=FakeSource(), sinks=[], ignore_rules=rules)


def _logs(*messages):
    return [LogEntry(message=m, timestamp=i) for i, m in enumerate(messages)]


def test_no_rules_keeps_everything():
    logs = _logs("a", "b")
    assert filter_log_entries(_config([]), logs) == logs


def test_drops_matching_substring_case_insensitive():
    logs = _logs("read: Connection reset by peer", "Timeout", "CONNECTION RESET BY PEER")
    result = filter_log_entries(_config(["connection reset by peer"]), logs)
    assert [e.message for e in result] == ["Timeout"]


def test_multiple_rules_and_empty_rule_ignored():
    logs = _logs("boom", "bang", "keep")
    result = filter_log_entries(_config(["boom", "", "bang"]), logs)
    assert [e.message for e in result] == ["keep"]


def test_regex_rule_matches_anywhere_ignoring_case():
    logs = _logs("GET /x failed: Timeout after 3000ms", "Timeout", "ok")
    result = filter_log_entries(_config([r"re:timeout after \d+ms"]), logs)
    assert [e.message for e in result] == ["Timeout", "ok"]


def test_plain_rule_with_regex_chars_is_literal():
    logs = _logs("Error (code 5)", "Error code 5")
    result = filter_log_entries(_config(["Error (code 5)"]), logs)
    assert [e.message for e in result] == ["Error code 5"]


def test_build_ignore_rules_accepts_none_and_valid():
    assert build_ignore_rules(None) == []
    assert build_ignore_rules(["abc", r"re:\d+"]) == ["abc", r"re:\d+"]


def test_build_ignore_rules_rejects_invalid_regex():
    with pytest.raises(ValueError, match="Invalid ignore regex"):
        build_ignore_rules(["re:("])
