import os
import csv
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import httpx

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "test_cases.csv")


def load_perf_cases():
    cases = []
    path = os.path.abspath(CSV_PATH)
    if not os.path.exists(path):
        return cases
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['ID'].startswith('TP-16') or r['ID'].startswith('TP-17') or r['ID'].startswith('TP-18') or r['ID'].startswith('TP-19') or r['ID'].startswith('TP-20'):
                cases.append(r)
    return cases


def _post(client, payload):
    start = time.perf_counter()
    r = client.post("/api/bureau/consultar", json=payload)
    elapsed = (time.perf_counter() - start) * 1000.0
    return r.status_code, elapsed


@pytest.mark.performance
def test_performance_quick_check():
    """Quick perf smoke: run a small batch and assert median latency under threshold.

    The performance tests are opt-in: set environment variable `RUN_PERF=1` to execute.
    """
    if os.getenv("RUN_PERF") != "1":
        pytest.skip("Performance tests skipped (set RUN_PERF=1 to enable)")

    perf_cases = load_perf_cases()
    assert perf_cases, "No performance cases found in docs/test_cases.csv"

    # Using a small thread pool to simulate concurrency for smoke test
    concurrency = int(os.getenv("PERF_CONCURRENCY", "10"))
    requests_per_worker = int(os.getenv("PERF_REQUESTS_PER_WORKER", "5"))

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    latencies = []
    statuses = []

    payload = {"cliente_id": 1}

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        for _ in range(concurrency * requests_per_worker):
            futures.append(ex.submit(_post, client, payload))

        for fut in as_completed(futures):
            status, elapsed = fut.result()
            statuses.append(status)
            latencies.append(elapsed)

    client.close()

    # Basic assertions
    ok_ratio = sum(1 for s in statuses if 200 <= s < 300) / len(statuses)
    median_ms = statistics.median(latencies) if latencies else float('inf')

    # Acceptable smoke thresholds (configurable via env)
    min_ok_ratio = float(os.getenv("PERF_MIN_OK_RATIO", "0.98"))
    max_median_ms = float(os.getenv("PERF_MAX_MEDIAN_MS", "500"))

    assert ok_ratio >= min_ok_ratio, f"High error rate in performance smoke: ok_ratio={ok_ratio}"
    assert median_ms <= max_median_ms, f"Median latency too high: {median_ms}ms (threshold {max_median_ms}ms)"
