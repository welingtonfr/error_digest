import json

MAX_SPANS = 40
MAX_VALUE_LENGTH = 200
NS_PER_MS = 1e6

# Attributes worth showing in the summary (both old and new OTel conventions).
USEFUL_ATTRIBUTES = (
    "http.method",
    "http.request.method",
    "http.route",
    "http.target",
    "url.path",
    "http.status_code",
    "http.response.status_code",
    "db.system",
    "db.statement",
    "db.query.text",
    "db.operation",
    "rpc.method",
    "messaging.destination",
)
ERROR_STATUS_CODES = {2, "STATUS_CODE_ERROR", "ERROR"}


def _attribute_value(value: dict):
    for type_key in ("stringValue", "intValue", "boolValue", "doubleValue"):
        if type_key in value:
            return value[type_key]
    return None


def _attributes_to_dict(attributes: list[dict] | None) -> dict:
    return {
        attribute["key"]: _attribute_value(attribute.get("value", {}))
        for attribute in attributes or []
    }


def _truncate(value, max_length: int = MAX_VALUE_LENGTH) -> str:
    text = str(value).replace("\n", " ")
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def _find_resource_spans(trace_json: dict) -> list[dict]:
    trace_json = trace_json.get("trace", trace_json)
    return trace_json.get("resourceSpans") or trace_json.get("batches") or []


def _collect_spans(trace_json: dict) -> list[dict]:
    """Flatten the trace into a list of spans, tagging each with its service."""
    spans: list[dict] = []

    for resource_span in _find_resource_spans(trace_json):
        resource_attributes = _attributes_to_dict(
            resource_span.get("resource", {}).get("attributes")
        )
        service_name = resource_attributes.get("service.name", "?")

        scope_spans = (
            resource_span.get("scopeSpans")
            or resource_span.get("instrumentationLibrarySpans")
            or []
        )
        for scope_span in scope_spans:
            for span in scope_span.get("spans", []):
                spans.append({**span, "_service": service_name})

    return spans


def _start_ns(span: dict) -> int:
    return int(span.get("startTimeUnixNano", 0))


def _end_ns(span: dict) -> int:
    return int(span.get("endTimeUnixNano", 0))


def _is_error(span: dict) -> bool:
    return span.get("status", {}).get("code") in ERROR_STATUS_CODES


def _pick_spans(spans: list[dict], max_spans: int) -> list[dict]:
    """Keep error spans first, fill the rest in order, then sort by start time."""
    error_spans = [span for span in spans if _is_error(span)]
    ok_spans = [span for span in spans if not _is_error(span)]
    picked = (error_spans + ok_spans)[:max_spans]
    return sorted(picked, key=_start_ns)


def _format_span(span: dict, trace_start_ns: int) -> str:
    offset_ms = (_start_ns(span) - trace_start_ns) / NS_PER_MS
    duration_ms = (_end_ns(span) - _start_ns(span)) / NS_PER_MS
    marker = "!" if _is_error(span) else "-"

    line = (
        f"{marker} +{offset_ms:.0f}ms {duration_ms:.0f}ms "
        f"{span['_service']} {span.get('name', '?')}"
    )

    attributes = _attributes_to_dict(span.get("attributes"))
    useful = {
        name: _truncate(attributes[name])
        for name in USEFUL_ATTRIBUTES
        if name in attributes
    }
    if useful:
        line += " " + " ".join(f"{name}={value}" for name, value in useful.items())

    error_message = span.get("status", {}).get("message")
    if _is_error(span) and error_message:
        line += f" | {_truncate(error_message)}"

    return line


def _format_exceptions(span: dict) -> list[str]:
    lines = []
    for event in span.get("events", []):
        if event.get("name") != "exception":
            continue
        event_attributes = _attributes_to_dict(event.get("attributes"))
        exception_type = event_attributes.get("exception.type", "?")
        exception_message = _truncate(event_attributes.get("exception.message", ""))
        lines.append(f"    exception {exception_type}: {exception_message}")
    return lines


def summarize_trace_otlp(raw: str, max_spans: int = MAX_SPANS) -> str:
    """Compact the OTLP JSON returned by Tempo into a short, readable text."""
    try:
        trace_json = json.loads(raw)
    except ValueError:
        return _truncate(raw, 2000)

    spans = _collect_spans(trace_json)
    if not spans:
        return "(trace without spans)"

    spans.sort(key=_start_ns)
    trace_start_ns = _start_ns(spans[0])
    error_count = sum(_is_error(span) for span in spans)
    shown_spans = _pick_spans(spans, max_spans)

    lines = [f"trace: {len(spans)} spans, {error_count} with error"]
    for span in shown_spans:
        lines.append(_format_span(span, trace_start_ns))
        lines.extend(_format_exceptions(span))

    omitted = len(spans) - len(shown_spans)
    if omitted > 0:
        lines.append(f"... {omitted} more spans omitted")

    return "\n".join(lines)
