from collections import defaultdict, deque
from threading import Lock

_lock = Lock()
_request_counts = defaultdict(int)
_status_counts = defaultdict(int)
_latency_samples = deque(maxlen=1000)


def record_request(method: str, path: str, status_code: int, latency_ms: float) -> None:
    route_key = f"{method} {path}"

    with _lock:
        _request_counts[route_key] += 1
        _status_counts[str(status_code)] += 1
        _latency_samples.append(float(latency_ms))


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    index = int(round((percentile / 100) * (len(values) - 1)))
    return round(values[index], 2)


def get_metrics_snapshot() -> dict:
    with _lock:
        latencies = list(_latency_samples)
        request_counts = dict(_request_counts)
        status_counts = dict(_status_counts)

    return {
        "total_requests": sum(request_counts.values()),
        "request_counts": request_counts,
        "status_counts": status_counts,
        "latency_ms": {
            "p95": _percentile(latencies, 95),
            "p99": _percentile(latencies, 99),
            "sample_size": len(latencies),
        },
    }
