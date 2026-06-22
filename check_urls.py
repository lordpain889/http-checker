#!/usr/bin/env python3
"""Check HTTP status for URLs listed in a text file."""

import argparse
import csv
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

DEFAULT_INPUT = "urls.txt"
DEFAULT_OUTPUT = "results.csv"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 2


def load_urls(path: Path) -> list[str]:
    if not path.exists():
        print(f"Error: input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    urls: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            url = line.strip()
            if url and not url.startswith("#"):
                urls.append(url)

    if not urls:
        print(f"Error: no URLs found in {path}", file=sys.stderr)
        sys.exit(1)

    return urls


def is_valid_http_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_url(url: str, timeout: int, retries: int) -> tuple[int | None, float | None, str]:
    start = time.perf_counter()
    last_error = ""

    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            elapsed = time.perf_counter() - start
            if response.status_code >= 500 and attempt < retries:
                last_error = f"Server error {response.status_code}"
                continue
            return response.status_code, round(elapsed, 3), ""
        except requests.exceptions.Timeout:
            last_error = "Timeout"
        except requests.exceptions.ConnectionError as exc:
            last_error = f"Connection error: {exc.__class__.__name__}"
        except requests.exceptions.RequestException as exc:
            last_error = str(exc)

        if attempt < retries:
            time.sleep(0.25 * (attempt + 1))

    elapsed = time.perf_counter() - start
    return None, round(elapsed, 3), f"{last_error} (after {retries + 1} attempts)"


def save_results(path: Path, rows: list[dict[str, str | int | float | None]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["URL", "Status Code", "Response Time", "Error"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send HTTP GET requests to URLs and save results to CSV."
    )
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_INPUT,
        help=f"Input file with one URL per line (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output CSV file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Retries for timeout/5xx errors (default: {DEFAULT_RETRIES})",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    urls = load_urls(input_path)
    total = len(urls)
    results: list[dict[str, str | int | float | None]] = []

    print(
        f"Checking {total} URL(s) with a {args.timeout}s timeout and {max(0, args.retries)} retries...\n"
    )

    for index, url in enumerate(urls, start=1):
        if not is_valid_http_url(url):
            status_code, response_time, error = None, None, "Invalid URL (must start with http:// or https://)"
        else:
            status_code, response_time, error = check_url(url, args.timeout, max(0, args.retries))
        row = {
            "URL": url,
            "Status Code": status_code if status_code is not None else "",
            "Response Time": response_time if response_time is not None else "",
            "Error": error,
        }
        results.append(row)

        if error:
            print(f"[{index}/{total}] {url} -> ERROR ({error})")
        else:
            print(
                f"[{index}/{total}] {url} -> {status_code} "
                f"({response_time}s)"
            )

    save_results(output_path, results)
    print(f"\nDone. Results saved to {output_path}")


if __name__ == "__main__":
    main()
