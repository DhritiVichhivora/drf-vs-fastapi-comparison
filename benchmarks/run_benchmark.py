"""
Runs the same Locust load test against each server setup, several times,
and saves the results to benchmarks/results.json.

Usage (from the project root, with the virtual environment active):
    python benchmarks/run_benchmark.py              # full run
    python benchmarks/run_benchmark.py --quick      # short test run to check it works
"""
import argparse
import csv
import json
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = Path(__file__).resolve().parent
RAW = BENCH / "raw"

PY = sys.executable

# name -> (folder to run in, command, port)
SETUPS = {
    "FastAPI (uvicorn)": (
        ROOT / "fastapi_app",
        [PY, "-m", "uvicorn", "main:app", "--port", "8000", "--log-level", "warning"],
        8000,
    ),
    "DRF (uvicorn)": (
        ROOT / "drf_app",
        [PY, "-m", "uvicorn", "config.asgi:application", "--port", "8001", "--log-level", "warning"],
        8001,
    ),
    "DRF (waitress)": (
        ROOT / "drf_app",
        [PY, "-m", "waitress", "--port=8001", "config.wsgi:application"],
        8001,
    ),
}


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for(port, seconds=30):
    end = time.time() + seconds
    while time.time() < end:
        if port_open(port):
            return True
        time.sleep(0.3)
    return False


def run_locust(port, users, spawn_rate, duration, prefix):
    cmd = [
        PY, "-m", "locust", "-f", str(BENCH / "locustfile.py"),
        "--headless", "-u", str(users), "-r", str(spawn_rate), "-t", f"{duration}s",
        "--host", f"http://127.0.0.1:{port}", "--csv", str(prefix), "--only-summary",
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    with open(f"{prefix}_stats.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["Name"] == "Aggregated":
                return {
                    "requests": int(row["Request Count"]),
                    "failures": int(row["Failure Count"]),
                    "rps": round(float(row["Requests/s"]), 1),
                    "median_ms": float(row["50%"]),
                    "p95_ms": float(row["95%"]),
                }
    raise RuntimeError("No results found in Locust CSV")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="short test run")
    args = ap.parse_args()

    users, spawn, duration, repeats = (10, 10, 5, 1) if args.quick else (50, 10, 30, 3)
    RAW.mkdir(exist_ok=True)
    results = {}

    for name, (folder, cmd, port) in SETUPS.items():
        if port_open(port):
            sys.exit(f"Port {port} is already in use. Stop any running server first, then try again.")
        print(f"\n=== {name} ===")
        server = subprocess.Popen(cmd, cwd=folder, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            if not wait_for(port):
                sys.exit(f"Server for {name} did not start. Check that it runs on its own first.")
            time.sleep(1)
            # warm-up so the first requests do not skew the numbers
            run_locust(port, 5, 5, 3, RAW / "warmup")
            runs = []
            for i in range(1, repeats + 1):
                prefix = RAW / (name.replace(" ", "_").replace("(", "").replace(")", "") + f"_run{i}")
                r = run_locust(port, users, spawn, duration, prefix)
                runs.append(r)
                print(f"  run {i}: {r['rps']} req/s, median {r['median_ms']} ms, "
                      f"p95 {r['p95_ms']} ms, failures {r['failures']}")
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
            time.sleep(1)

        results[name] = {
            "runs": runs,
            "average": {
                "rps": round(statistics.mean(r["rps"] for r in runs), 1),
                "median_ms": round(statistics.mean(r["median_ms"] for r in runs), 1),
                "p95_ms": round(statistics.mean(r["p95_ms"] for r in runs), 1),
                "failures": sum(r["failures"] for r in runs),
            },
        }

    out = {"settings": {"users": users, "duration_seconds": duration, "runs_per_setup": repeats},
           "results": results}
    (BENCH / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("\n=== SUMMARY (average of runs) ===")
    print(f"{'Setup':20} {'req/s':>8} {'median ms':>10} {'p95 ms':>8} {'failures':>9}")
    for name, v in results.items():
        a = v["average"]
        print(f"{name:20} {a['rps']:>8} {a['median_ms']:>10} {a['p95_ms']:>8} {a['failures']:>9}")
    print("\nSaved to benchmarks/results.json")


if __name__ == "__main__":
    main()
