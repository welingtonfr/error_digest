from error_digest.core.fingerprint import fingerprint, group_by_fingerprint, normalize
from error_digest.core.models import LogEntry


def test_same_error_different_ids_same_fingerprint():
    a = "User 123 not found: id=550e8400-e29b-41d4-a716-446655440000"
    b = "User 987 not found: id=123e4567-e89b-12d3-a456-426614174000"
    assert fingerprint(a) == fingerprint(b)


def test_different_errors_different_fingerprint():
    assert fingerprint("Timeout calling payments") != fingerprint("Column not found")


def test_sql_values_and_codes():
    msg = "SQLSTATE[42S22]: Column not found 'quantity' in 'where clause'"
    assert "42S22" in normalize(msg)
    assert "quantity" not in normalize(msg)


def test_group_counts_order_and_trace():
    e = lambda m, ts, t=None: LogEntry(message=m, timestamp=ts, trace_id=t)  # noqa: E731
    groups = group_by_fingerprint(
        [e("Boom 1", 1, "t1"), e("Other", 2), e("Boom 2", 3, "t3"), e("Boom 3", 4)]
    )
    assert [g.count for g in groups] == [3, 1]
    assert groups[0].trace_id == "t3"
    assert groups[0].first_seen == 1 and groups[0].last_seen == 4
