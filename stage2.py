#!/usr/bin/env python3
"""
test_proxies.py

Reads proxy list from 'proxy.txt' (one per line, like 45.143.99.15:80 or 45.143.99.15:80)
Tests proxies concurrently and prints status.
Supports HTTP and SOCKS4/5 proxies automatically.
Outputs a Python-style list of active proxies and writes them to 'active_proxies.txt'.

Usage:
    pip install requests[socks]
    python3 test_proxies.py
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

INPUT_FILE = "active_proxies.txt"
OUTPUT_FILE = "active_proxies.txt"
TEST_URL = "https://httpbin.org/ip"
TIMEOUT = 6
MAX_WORKERS = 500


def normalize_proxy(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    # Detect if port 1080 or similar => likely SOCKS5
    if line.startswith(("", "https://", "", "")):
        return line
    if ":1080" in line:
        return "" + line
    return "" + line


def is_proxy_alive(proxy: str) -> tuple:
    proxies = {"http": proxy, "https": proxy}
    start = time.time()
    try:
        r = requests.get(TEST_URL, proxies=proxies, timeout=TIMEOUT)
        elapsed = time.time() - start
        if r.status_code == 200:
            return proxy, True, elapsed, None
        else:
            return proxy, False, elapsed, f"status {r.status_code}"
    except Exception as e:
        elapsed = time.time() - start
        return proxy, False, elapsed, str(e)


def load_proxies(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        lines = [normalize_proxy(l) for l in f.readlines()]
    # remove duplicates & empties
    seen = set()
    out = []
    for p in lines:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def main():
    proxies = load_proxies(INPUT_FILE)
    if not proxies:
        print("No proxies found in", INPUT_FILE)
        return

    print(f"Loaded {len(proxies)} proxies. Testing with {MAX_WORKERS} threads...\n")

    active = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = [exe.submit(is_proxy_alive, p) for p in proxies]
        for fut in as_completed(futures):
            proxy, alive, elapsed, err = fut.result()
            if alive:
                print(f"Active: '{proxy}'  (rtt: {elapsed:.2f}s)")
                active.append(proxy)
            else:
                err_short = err if err is None else (err if len(err) < 120 else err[:117] + "...")
                print(f"Dead:   '{proxy}'  ({err_short})")

    # Print working proxies in list format
    print("\nActive proxies in Python list format:\n")
    print("proxies_list = [")
    for p in active:
        print(f'    "{p}",')
    print("]\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for p in active:
            f.write(p + "\n")

    print(f"Found {len(active)} active proxies. Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
