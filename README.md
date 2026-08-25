# TCP Port Scanner

A small Python TCP connect scanner. The current script checks ports **1–1000** on the hard-coded host `scanme.nmap.org`, classifies each connection attempt, and tries to collect a passive banner from open ports.

> **Authorized use only:** Scan only systems you own or systems for which you have explicit permission. Confirm the approved target, port range, rate, timing, and testing conditions before running a scan. TCP connection attempts can be logged, trigger alerts, or affect fragile services. Follow all applicable laws, policies, and provider terms. The default host is a public scan-testing host, but you should still review and respect its published rules; its presence in this script does not imply permission to scan any other system.

## Current behavior

Running `main.py` immediately:

1. Creates up to 200 worker threads.
2. Attempts full IPv4 TCP connections to ports 1 through 1000 on `scanme.nmap.org`.
3. Limits the start of connection attempts to approximately 50 per second across all workers.
4. Applies a one-second timeout to each blocking socket operation (the connection attempt and, for an open port, the banner read).
5. Classifies a port as:
   - `open` when the connection succeeds;
   - `closed` when the connection is explicitly refused; or
   - `filtered` on a timeout or any other numeric connection result.
6. For an open port, waits for up to 1,024 bytes sent by the service without first sending a request. If no banner arrives, it uses the local system's service-name database as a fallback, or `Unknown` if no mapping exists.

Although all work is submitted to the thread pool immediately, the rate limiter spaces connection starts by 0.02 seconds. Starting all 1,000 connection attempts therefore takes about 20 seconds, and connection timeouts or banner reads can make the complete run longer.

## Requirements

- Python 3
- No third-party packages; only the Python standard library is used
- DNS resolution and network access to the configured target

The scanner uses normal TCP connections and does not require raw-socket or administrator/root privileges under typical system policies.

## Usage

From the project directory:

```bash
python3 main.py
```

On systems where the Python 3 executable is named `python`:

```bash
python main.py
```

There are no supported command-line arguments, prompts, environment variables, or configuration files. Importing `main.py` also starts the scan because execution is at module level.

## Configuration

All settings are hard-coded in `main.py`:

| Setting | Current value |
| --- | --- |
| Target | `scanme.nmap.org` |
| Address family / protocol | IPv4 TCP |
| Port range | 1–1000, inclusive |
| Socket timeout | 1 second per blocking socket operation |
| Connection start rate | 50 per second |
| Maximum worker threads | 200 |
| Maximum banner read | 1,024 bytes |

Changing these values requires editing the source. The project does not validate custom targets or ranges and has no runtime safety confirmation. Before changing the target or scan characteristics, obtain explicit authorization and keep the rate and scope within the agreed limits.

## Output

The script prints two Python list representations to standard output:

1. A list of `(port, state)` tuples for all scanned ports.
2. A list of `(port, banner_or_service_name)` tuples for open ports only.

Illustrative shape (not actual scan results):

```text
[(22, 'open'), (1, 'closed'), (3, 'filtered'), ...]
[(22, 'SSH-2.0-example'), ...]
```

Results are appended as worker threads finish, so neither list is guaranteed to be sorted by port. Output is not JSON, CSV, or written to a file.

A fallback service name is only a local database lookup based on the port number. It is not proof that the named service is actually running on that port.

## Known limitations

- Scans only the fixed IPv4 TCP target and port range; there is no IPv6 or UDP support.
- Does not accept a target, port range, timeout, rate, or output format at runtime.
- Performs a full TCP connect scan rather than a SYN/raw-packet scan.
- Uses coarse status classification: results other than success or explicit refusal are labeled `filtered`, even when another network error may be the cause.
- Makes no retries and does not distinguish packet loss, firewall filtering, routing failures, and other connectivity problems.
- Banner collection is passive. Many protocols send nothing until a client request is made, so a real service banner may be unavailable.
- Banner bytes are decoded as text with undecodable bytes discarded.
- Service-name fallbacks depend on the machine's local service database and may be missing or misleading.
- DNS resolution is performed as part of each connection attempt and is not necessarily bounded by the socket timeout.
- Unhandled DNS, socket, or worker exceptions can terminate the run before output is printed.
- Keeps all results in memory and prints only after every submitted task has completed.
- Provides no progress display, structured reporting, persistence, logging, or automated tests.
