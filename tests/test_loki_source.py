from unittest.mock import MagicMock, patch

from error_digest.sources.loki_source import LokiSource


def _source():
    return LokiSource(
        url="http://g", grafana_key="k", datasource_uid="u", labels={"app": 'a"b'}
    )


def test_fetch_errors_sorted_lines():
    payload = {
        "data": {
            "result": [
                {"stream": {"trace_id": "T"}, "values": [["3", "c"], ["1", "a"]]},
                {"stream": {}, "values": [["2", "b"]]},
            ]
        }
    }
    resp = MagicMock()
    resp.json.return_value = payload
    with patch("error_digest.sources.loki_source.requests.get", return_value=resp) as g:
        entries = _source().fetch_errors("1h")
        assert [e.message for e in entries] == ["a", "b", "c"]
        assert [e.trace_id for e in entries] == ["T", None, "T"]
    params = g.call_args.kwargs["params"]
    assert params["direction"] == "backward"
    assert params["limit"] == 1000
    assert params["query"] == (
        '{app="a\\"b"} | detected_level=~"(?i)(error|critical|fatal)"'
    )
