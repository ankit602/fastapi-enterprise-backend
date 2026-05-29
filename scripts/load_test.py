import argparse
import json
import statistics
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def call_api(url: str) -> tuple[int, float]:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            status_code = response.status
            response.read()
    except Exception:
        status_code = 0

    latency_ms = (time.perf_counter() - start) * 1000
    return status_code, latency_ms


def percentile(values: list[float], value: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    index = int(round((value / 100) * (len(values) - 1)))
    return round(values[index], 2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Small API load test with p95/p99 latency.")
    parser.add_argument("--url", default="http://127.0.0.1:8001/api/v1/employees/?page=1&limit=10")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()

    started_at = time.perf_counter()
    latencies = []
    status_counts = {}

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(call_api, args.url) for _ in range(args.requests)]
        for future in as_completed(futures):
            status_code, latency_ms = future.result()
            latencies.append(latency_ms)
            status_counts[str(status_code)] = status_counts.get(str(status_code), 0) + 1

    total_seconds = time.perf_counter() - started_at
    result = {
        "url": args.url,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "duration_seconds": round(total_seconds, 2),
        "requests_per_second": round(args.requests / total_seconds, 2),
        "status_counts": status_counts,
        "latency_ms": {
            "avg": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
