import os
import csv
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
CONCURRENCY = int(os.getenv("PERF_CONCURRENCY", "20"))
REQUESTS_PER_WORKER = int(os.getenv("PERF_REQUESTS_PER_WORKER", "5"))
CSV_OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "test_results.csv"))


def _post(client, payload):
    start = time.perf_counter()
    try:
        r = client.post("/api/bureau/consultar", json=payload)
        status = r.status_code
    except Exception:
        status = 0
    elapsed = (time.perf_counter() - start) * 1000.0
    return status, elapsed


def run():
    total_requests = CONCURRENCY * REQUESTS_PER_WORKER
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    latencies = []
    statuses = []
    payload = {"cliente_id": 1}

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = [ex.submit(_post, client, payload) for _ in range(total_requests)]
        for fut in as_completed(futures):
            status, elapsed = fut.result()
            statuses.append(status)
            latencies.append(elapsed)

    client.close()

    successful = sum(1 for s in statuses if 200 <= s < 300)
    failed = total_requests - successful
    ok_ratio = successful / total_requests if total_requests else 0
    median_ms = statistics.median(latencies) if latencies else None

    row = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "base_url": BASE_URL,
        "concurrency": CONCURRENCY,
        "requests_per_worker": REQUESTS_PER_WORKER,
        "total_requests": total_requests,
        "successful": successful,
        "failed": failed,
        "ok_ratio": f"{ok_ratio:.4f}",
        "median_ms": f"{median_ms:.2f}" if median_ms is not None else "",
    }

    write_header = not os.path.exists(CSV_OUT)
    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    with open(CSV_OUT, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print("Perf summary:", row)


if __name__ == "__main__":
    run()
