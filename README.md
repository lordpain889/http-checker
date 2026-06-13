# HTTP Checker

A simple Python script that reads URLs from a text file, sends HTTP GET requests to each one, and saves the results to a CSV file.

## Features

- Reads URLs from `urls.txt` (one URL per line)
- Sends HTTP GET requests with a 10 second timeout
- Handles connection errors and timeouts gracefully
- Saves results to CSV with columns: URL, Status Code, Response Time, Error
- Shows progress in the terminal

## Setup

1. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   - Windows (PowerShell):

     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

   - macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Add URLs to `urls.txt`, one per line. Lines starting with `#` are ignored.

2. Run the checker:

   ```bash
   python check_urls.py
   ```

3. Results are written to `results.csv`.

### Options

```bash
python check_urls.py --help
```

| Option | Default | Description |
|--------|---------|-------------|
| `-i`, `--input` | `urls.txt` | Input file with URLs |
| `-o`, `--output` | `results.csv` | Output CSV file |
| `-t`, `--timeout` | `10` | Request timeout in seconds |

### Examples

```bash
python check_urls.py -i my-urls.txt -o output.csv
python check_urls.py --timeout 5
```

## Output

The CSV file contains these columns:

| Column | Description |
|--------|-------------|
| URL | The checked URL |
| Status Code | HTTP status code (empty on error) |
| Response Time | Time in seconds to receive a response |
| Error | Error message if the request failed |

## Sample Output

```
Checking 4 URL(s) with a 10s timeout...

[1/4] https://httpbin.org/status/200 -> 200 (0.842s)
[2/4] https://httpbin.org/status/404 -> 404 (0.651s)
[3/4] https://httpbin.org/delay/15 -> ERROR (Timeout)
[4/4] https://invalid-domain-that-does-not-exist.example -> ERROR (Connection error: ConnectionError)

Done. Results saved to results.csv
```
