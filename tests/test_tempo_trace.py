from unittest.mock import MagicMock, patch

from error_digest.traces.tempo_trace import TempoTrace


def _tempo():
    return TempoTrace(url="http://g", grafana_key="k", datasource_uid="tu")


def test_get_ok_and_404():
    ok = MagicMock(status_code=200, text='{"batches": []}')
    missing = MagicMock(status_code=404)
    with patch("error_digest.traces.tempo_trace.requests.get") as g:
        g.return_value = ok
        assert _tempo().get("abc") == "(trace without spans)"
        assert (
            g.call_args.args[0]
            == "http://g/api/datasources/proxy/uid/tu/api/traces/abc"
        )
        g.return_value = missing
        assert _tempo().get("abc") is None


def test_summary_marks_error_span():
    import json

    from error_digest.traces.summary import summarize_trace_otlp

    raw = json.dumps(
        {
            "batches": [
                {
                    "resource": {
                        "attributes": [
                            {"key": "service.name", "value": {"stringValue": "api"}}
                        ]
                    },
                    "scopeSpans": [
                        {
                            "spans": [
                                {
                                    "name": "GET /x",
                                    "startTimeUnixNano": "1000000",
                                    "endTimeUnixNano": "9000000",
                                    "status": {},
                                },
                                {
                                    "name": "SELECT",
                                    "startTimeUnixNano": "2000000",
                                    "endTimeUnixNano": "3000000",
                                    "attributes": [
                                        {
                                            "key": "db.statement",
                                            "value": {"stringValue": "select 1"},
                                        }
                                    ],
                                    "status": {"code": 2, "message": "boom"},
                                    "events": [
                                        {
                                            "name": "exception",
                                            "attributes": [
                                                {
                                                    "key": "exception.type",
                                                    "value": {
                                                        "stringValue": "PDOException"
                                                    },
                                                },
                                                {
                                                    "key": "exception.message",
                                                    "value": {
                                                        "stringValue": "bad column"
                                                    },
                                                },
                                            ],
                                        }
                                    ],
                                },
                            ]
                        }
                    ],
                }
            ]
        }
    )
    out = summarize_trace_otlp(raw)
    assert "2 spans, 1 with error" in out
    assert "! +1ms 1ms api SELECT db.statement=select 1 | boom" in out
    assert "exception PDOException: bad column" in out
