#!/usr/bin/env python3
"""Check HTTP status for URLs listed in a text file."""

import argparse
import csv
import sys
import time
from pathlib import Path

import requests

DEFAULT_INPUT = "urls.txt"
DEFAULT_OUTPUT = "results.csv"
DEFAULT_TIMEOUT = 10


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


def check_url(url: str, timeout: int) -> tuple[int | None, float | None, str]:
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        elapsed = time.perf_counter() - start
        return response.status_code, round(elapsed, 3), ""
    except requests.exceptions.Timeout:
        elapsed = time.perf_counter() - start
        return None, round(elapsed, 3), "Timeout"
    except requests.exceptions.ConnectionError as exc:
        elapsed = time.perf_counter() - start
        return None, round(elapsed, 3), f"Connection error: {exc.__class__.__name__}"
    except requests.exceptions.RequestException as exc:
        elapsed = time.perf_counter() - start
        return None, round(elapsed, 3), str(exc)


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
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    urls = load_urls(input_path)
    total = len(urls)
    results: list[dict[str, str | int | float | None]] = []

    print(f"Checking {total} URL(s) with a {args.timeout}s timeout...\n")

    for index, url in enumerate(urls, start=1):
        status_code, response_time, error = check_url(url, args.timeout)
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
