import socket
import concurrent.futures
import time

# Common ports and their services
COMMON_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 3306: "MySQL",
    3389: "RDP", 8080: "HTTP-ALT", 8443: "HTTPS-ALT"
}

# Banner grabbing - get service info
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

# Scan a single port with timeout and retry
def scan_port(ip, port, timeout=1, retries=2):
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result == 0:
                # Port is open
                service = COMMON_SERVICES.get(port, "Unknown")
                banner = grab_banner(ip, port)
                return {
                    "port": port,
                    "status": "OPEN",
                    "service": service,
                    "banner": banner
                }
        except socket.error:
            time.sleep(0.1)  # wait before retry
    return {"port": port, "status": "CLOSED", "service": "", "banner": ""}

# Concurrent scanner
def scan_ports(ip, start_port, end_port, max_threads=100):
    print(f"\n{'='*60}")
    print(f"  Custom Port Scanner - Target: {ip}")
    print(f"  Scanning ports {start_port} to {end_port}")
    print(f"{'='*60}\n")

    open_ports = []
    start_time = time.time()

    ports = list(range(start_port, end_port + 1))

    # Use ThreadPoolExecutor for concurrent scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_port, ip, port): port for port in ports}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            completed += 1
            # Progress indicator
            print(f"\rScanning... {completed}/{len(ports)} ports", end="", flush=True)
            if result["status"] == "OPEN":
                open_ports.append(result)

    end_time = time.time()
    elapsed = round(end_time - start_time, 2)

    # Print results
    print(f"\n\n{'='*60}")
    print(f"  SCAN RESULTS")
    print(f"{'='*60}")
    print(f"{'PORT':<10}{'STATUS':<10}{'SERVICE':<15}{'BANNER'}")
    print(f"{'-'*60}")

    if open_ports:
        for p in sorted(open_ports, key=lambda x: x["port"]):
            print(f"{p['port']:<10}{p['status']:<10}{p['service']:<15}{p['banner']}")
    else:
        print("  No open ports found.")

    print(f"\n{'='*60}")
    print(f"  Scan Efficiency Report")
    print(f"{'='*60}")
    print(f"  Total Ports Scanned : {len(ports)}")
    print(f"  Open Ports Found    : {len(open_ports)}")
    print(f"  Time Taken          : {elapsed} seconds")
    print(f"  Threads Used        : {max_threads}")
    print(f"  Ports/Second        : {round(len(ports)/elapsed, 2)}")
    print(f"{'='*60}\n")

# Main
if __name__ == "__main__":
    print("="*60)
    print("     CUSTOM PORT SCANNER WITH SERVICE DETECTION")
    print("="*60)
    
    target = input("\nEnter Target IP (or 'localhost'): ").strip()
    start  = int(input("Enter Start Port (e.g. 1): "))
    end    = int(input("Enter End Port   (e.g. 1024): "))

    # Resolve hostname to IP
    try:
        ip = socket.gethostbyname(target)
        print(f"\n  Resolved: {target} → {ip}")
    except socket.gaierror:
        print("  Invalid host!")
        exit()

    scan_ports(ip, start, end)