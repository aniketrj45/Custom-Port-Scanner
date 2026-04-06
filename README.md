# 🔍 Custom Port Scanner with Service Detection

> A fast, concurrent TCP port scanner with banner grabbing and service identification — built in Python using multithreading.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Threads](https://img.shields.io/badge/Threads-Concurrent-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📋 Table of Contents

1. [Problem Definition](#1-problem-definition)
2. [Architecture](#2-architecture)
3. [Core Implementation](#3-core-implementation)
4. [Features](#4-features)
5. [Performance Evaluation](#5-performance-evaluation)
6. [Optimization & Bug Fixes](#6-optimization--bug-fixes)
7. [Setup Instructions](#7-setup-instructions)
8. [Usage Guide](#8-usage-guide)
9. [Technical Documentation](#9-technical-documentation)
10. [Evaluation Criteria Mapping](#10-evaluation-criteria-mapping)
11. [License](#license)

---

## 1. Problem Definition

Network administrators and security professionals often need to audit which ports are open on a host, identify which services are running behind them, and assess exposure to potential vulnerabilities. Manual port checking is slow and error-prone at scale.

**This tool solves:**
- Identifying open TCP ports on a target host across a user-defined range
- Resolving which services are likely running on those ports (HTTP, SSH, FTP, etc.)
- Grabbing banners from open ports to reveal version/service metadata
- Doing all of this efficiently at scale using concurrent threads

**Constraints & Scope:**
- Protocol: TCP only (UDP support planned)
- Input: IP address or hostname + port range
- Output: Tabular report of open ports, service names, and banners
- Environment: Python 3.7+, no external dependencies

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        USER INPUT                            │
│           Target IP / Hostname  +  Port Range                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   DNS RESOLUTION                             │
│          socket.gethostbyname() → Resolved IP                │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│             CONCURRENT PORT SCANNING ENGINE                  │
│         ThreadPoolExecutor (max_workers=100)                 │
│                                                              │
│   Port 1 ──► scan_port()  ──► CLOSED                        │
│   Port 22 ─► scan_port()  ──► OPEN ──► grab_banner()        │
│   Port 80 ─► scan_port()  ──► OPEN ──► grab_banner()        │
│   Port N ──► scan_port()  ──► ...                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│               SERVICE IDENTIFICATION                         │
│         COMMON_SERVICES dict lookup (14 known ports)         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                  RESULTS DISPLAY                             │
│       PORT | STATUS | SERVICE | BANNER  +  Efficiency Report │
└──────────────────────────────────────────────────────────────┘
```

**Component Breakdown:**

| Component | Responsibility |
|---|---|
| `scan_port()` | Opens a TCP socket, attempts connection, returns open/closed status |
| `grab_banner()` | Sends HTTP HEAD request, reads up to 100 bytes of response |
| `scan_ports()` | Orchestrates threads, tracks progress, prints final report |
| `COMMON_SERVICES` | Dictionary mapping port numbers to service names |
| `__main__` | Entry point: user input, DNS resolution, scanner invocation |

---

## 3. Core Implementation

### 3.1 TCP Connect Scan (`scan_port`)

Uses `socket.connect_ex()` which returns `0` on success (port open) instead of raising an exception. Retries up to 2 times on socket errors with a 100ms delay.

```python
def scan_port(ip, port, timeout=1, retries=2):
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                service = COMMON_SERVICES.get(port, "Unknown")
                banner = grab_banner(ip, port)
                return {"port": port, "status": "OPEN", "service": service, "banner": banner}
        except socket.error:
            time.sleep(0.1)
    return {"port": port, "status": "CLOSED", "service": "", "banner": ""}
```

### 3.2 Banner Grabbing (`grab_banner`)

Reconnects to open ports and sends an HTTP HEAD request to capture the service banner (server header, version string, etc.). Truncates to 100 characters for clean output.

```python
def grab_banner(ip, port, timeout=2):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = sock.recv(1024).decode(errors="ignore").strip()
        sock.close()
        return banner[:100] if banner else "No banner"
    except:
        return "No banner"
```

### 3.3 Concurrent Scanning (`scan_ports`)

Uses `ThreadPoolExecutor` to scan multiple ports simultaneously. The `as_completed()` iterator processes results as they finish, enabling a real-time progress indicator.

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = {executor.submit(scan_port, ip, port): port for port in ports}
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result["status"] == "OPEN":
            open_ports.append(result)
```

### 3.4 Known Service Map

```python
COMMON_SERVICES = {
    21: "FTP",    22: "SSH",    23: "Telnet",  25: "SMTP",
    53: "DNS",    80: "HTTP",   110: "POP3",   143: "IMAP",
    443: "HTTPS", 445: "SMB",   3306: "MySQL",
    3389: "RDP",  8080: "HTTP-ALT", 8443: "HTTPS-ALT"
}
```

---

## 4. Features

- **Concurrent Scanning** — Up to 100 threads scan ports simultaneously, dramatically reducing total scan time
- **TCP Connect Scan** — Reliable full-connection scan using `connect_ex()` with configurable timeout
- **Retry Logic** — Automatically retries failed socket connections (default: 2 attempts) to reduce false negatives
- **Banner Grabbing** — Probes open ports with an HTTP HEAD request to capture service/version info
- **Service Identification** — Instantly maps 14 common ports to service names via a built-in dictionary
- **DNS Resolution** — Accepts both IP addresses and hostnames; auto-resolves to IP before scanning
- **Real-Time Progress** — Live `Scanning... X/N ports` indicator using carriage-return overwriting
- **Efficiency Report** — Prints total ports scanned, open ports found, time taken, and ports/second rate
- **Clean Tabular Output** — Results displayed in a formatted table: PORT | STATUS | SERVICE | BANNER

---

## 5. Performance Evaluation

### Benchmark Results (typical, on localhost)

| Port Range | Threads | Time (s) | Ports/Second |
|---|---|---|---|
| 1 – 100 | 100 | ~0.5s | ~200 |
| 1 – 1024 | 100 | ~2–4s | ~300–500 |
| 1 – 10000 | 100 | ~20–40s | ~250–500 |

> Results vary based on network latency, firewall response behavior, and system load.

### Bottlenecks Identified

| Bottleneck | Cause | Impact |
|---|---|---|
| Banner grabbing latency | Sequential per open port, 2s timeout | Adds ~2s per open port |
| Retry delay | 100ms sleep × 2 retries per failed port | Slows down scans with many filtered ports |
| Single HTTP probe | Only HTTP HEAD sent; non-HTTP services return "No banner" | Limited banner data for SSH, FTP, etc. |
| Thread saturation | Default 100 threads may not be enough for ranges > 5000 | Consider increasing `max_workers` |

### Efficiency Report (sample output)

```
============================================================
  Scan Efficiency Report
============================================================
  Total Ports Scanned : 1024
  Open Ports Found    : 3
  Time Taken          : 3.42 seconds
  Threads Used        : 100
  Ports/Second        : 299.42
============================================================
```

---

## 6. Optimization & Bug Fixes

### Optimizations Applied

**1. Thread Pool Concurrency**
Replaced sequential scanning with `ThreadPoolExecutor`, reducing scan time by 50–100× for large port ranges.

**2. Timeout Tuning**
Set `sock.settimeout(1)` for port scans and `sock.settimeout(2)` for banner grabs — balancing accuracy vs. speed. Increase for slow/remote targets.

**3. Banner Truncation**
Banner output truncated to 100 characters to prevent display overflow in the results table.

**4. Graceful Error Handling**
All socket operations are wrapped in try/except. Banner grabbing silently returns `"No banner"` on any failure to avoid crashing the thread.

### Known Issues & Planned Fixes

| Issue | Status | Fix |
|---|---|---|
| UDP scanning not supported | Planned | Add `SOCK_DGRAM` scan mode |
| Banner only probes HTTP | Planned | Add protocol-specific probes (FTP, SSH, SMTP) |
| No command-line arguments | Planned | Add `argparse` for scriptable/automated use |
| No output file export | Planned | Add `--output results.txt` / `--json` flag |
| No CIDR/subnet support | Planned | Allow scanning multiple hosts at once |
| Verbose mode missing | Planned | Add `--verbose` to show closed ports too |

---

## 7. Setup Instructions

### Prerequisites

- Python 3.7 or higher
- No external libraries required — uses only Python standard library modules:
  - `socket`
  - `concurrent.futures`
  - `time`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aniketrj45/Custom-Port-Scanner.git

# 2. Navigate into the project directory
cd Custom-Port-Scanner

# 3. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows

# 4. No pip install needed — zero external dependencies!
```

### Verify Python Version

```bash
python --version
# Should output Python 3.7.x or higher
```

---

## 8. Usage Guide

### Basic Usage

```bash
python scanner.py
```

You will be prompted interactively:

```
============================================================
     CUSTOM PORT SCANNER WITH SERVICE DETECTION
============================================================

Enter Target IP (or 'localhost'): 192.168.1.1
Enter Start Port (e.g. 1): 1
Enter End Port   (e.g. 1024): 1024

  Resolved: 192.168.1.1 → 192.168.1.1
```

### Example: Scan Localhost

```
Enter Target IP (or 'localhost'): localhost
Enter Start Port: 1
Enter End Port: 1024
```

### Example: Scan Remote Host

```
Enter Target IP (or 'localhost'): scanme.nmap.org
Enter Start Port: 1
Enter End Port: 500
```

### Sample Output

```
============================================================
  Custom Port Scanner - Target: 45.33.32.156
  Scanning ports 1 to 500
============================================================

Scanning... 500/500 ports

============================================================
  SCAN RESULTS
============================================================
PORT      STATUS    SERVICE        BANNER
------------------------------------------------------------
22        OPEN      SSH            No banner
80        OPEN      HTTP           HTTP/1.0 200 OK...
============================================================
  Scan Efficiency Report
============================================================
  Total Ports Scanned : 500
  Open Ports Found    : 2
  Time Taken          : 4.87 seconds
  Threads Used        : 100
  Ports/Second        : 102.67
============================================================
```

### Tips

- Use `localhost` or `127.0.0.1` to scan your own machine safely
- Start with a small port range (1–1024) before scanning wider ranges
- Increase `max_threads` in `scan_ports()` for faster scans on fast networks
- Always ensure you have **permission** to scan the target host

> ⚠️ **Legal Notice:** Only scan systems you own or have explicit written permission to test. Unauthorized port scanning may be illegal in your jurisdiction.

---

## 9. Technical Documentation

### Module: `scanner.py`

#### Constants

| Name | Type | Description |
|---|---|---|
| `COMMON_SERVICES` | `dict[int, str]` | Maps port numbers to service name strings |

#### Functions

---

#### `grab_banner(ip, port, timeout=2) → str`

Attempts to retrieve a service banner from an open port.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ip` | `str` | required | Target IP address |
| `port` | `int` | required | Port number to probe |
| `timeout` | `float` | `2` | Socket timeout in seconds |

**Returns:** Banner string (truncated to 100 chars), or `"No banner"` on failure.

**Behavior:** Sends `HEAD / HTTP/1.0\r\n\r\n` and reads up to 1024 bytes. Decodes with `errors="ignore"`.

---

#### `scan_port(ip, port, timeout=1, retries=2) → dict`

Scans a single port and returns its status.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ip` | `str` | required | Target IP address |
| `port` | `int` | required | Port number to scan |
| `timeout` | `float` | `1` | Connection timeout in seconds |
| `retries` | `int` | `2` | Number of retry attempts on failure |

**Returns:**
```python
# Open port
{"port": 80, "status": "OPEN", "service": "HTTP", "banner": "HTTP/1.0 200 OK..."}

# Closed port
{"port": 81, "status": "CLOSED", "service": "", "banner": ""}
```

---

#### `scan_ports(ip, start_port, end_port, max_threads=100) → None`

Main scanning orchestrator. Launches concurrent scan and prints results.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `ip` | `str` | required | Resolved target IP |
| `start_port` | `int` | required | First port in range (inclusive) |
| `end_port` | `int` | required | Last port in range (inclusive) |
| `max_threads` | `int` | `100` | Thread pool size |

**Side Effects:** Prints live progress, results table, and efficiency report to stdout.

---

### Flow Diagram

```
main()
  └─► input() × 3
  └─► socket.gethostbyname()
  └─► scan_ports(ip, start, end)
        └─► ThreadPoolExecutor
              └─► scan_port(ip, port) × N  [concurrent]
                    └─► socket.connect_ex()
                    └─► grab_banner()  [if OPEN]
        └─► print results table
        └─► print efficiency report
```

---

## 10. Evaluation Criteria Mapping

| Criteria | Implementation | Location |
|---|---|---|
| **Correctness** | `connect_ex()` returns 0 only on successful TCP handshake | `scan_port()` |
| **Efficiency** | `ThreadPoolExecutor` with 100 concurrent threads | `scan_ports()` |
| **Reliability** | Retry logic (2 attempts) + per-socket timeout | `scan_port()` |
| **Error Handling** | All sockets wrapped in try/except; silent fallbacks | All functions |
| **Service Detection** | Dict lookup across 14 common ports | `COMMON_SERVICES` |
| **Banner Grabbing** | HTTP HEAD probe on each open port | `grab_banner()` |
| **User Experience** | Live progress counter + formatted results table | `scan_ports()` |
| **Performance Metrics** | Ports/second, total time, thread count reported | Efficiency Report |
| **Portability** | Zero external dependencies, standard library only | Whole module |
| **Scalability** | `max_threads` is configurable; works on any port range | `scan_ports()` |

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---