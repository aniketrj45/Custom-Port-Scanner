Custom Port Scanner with Service Detection
Socket Programming - Jackfruit Mini Project

1. Problem Definition
The objective of this project is to implement a secure, high-performance network scanner using low-level TCP socket programming. Unlike high-level tools, this "Custom" scanner demonstrates:
+1


Manual Connection Handling: Explicit socket creation, binding, and connection management.


Concurrency: Scanning multiple ports simultaneously using a thread pool.
+1

Service Identification: Using "Banner Grabbing" to identify running software.


Security: SSL/TLS implementation for secure data exchange.

2. Architecture
The system follows a Multi-Threaded Client-Server architecture:

Target Resolution: Resolves hostnames to IP addresses using DNS.


Concurrency Engine: Utilizes ThreadPoolExecutor to manage 100+ concurrent worker threads.

TCP Probing: Each worker performs a TCP Three-Way Handshake with a specific port.


Banner Grabbing & SSL: If a port is open, the scanner establishes an SSL/TLS wrapped connection to safely retrieve the service banner.

3. Features
Full TCP Scan: Detects open/closed ports using low-level sockets.

Service Detection: Banner grabbing to identify FTP, SSH, HTTP, etc..

Robustness: Includes built-in timeout and retry logic to handle unstable network conditions.


Secure Communication: Implements SSL/TLS for mandatory secure control exchanges.

4. Setup & Usage
Prerequisites
Python 3.x

Git

Installation
Bash
git clone https://github.com/[your-username]/jackfruit-port-scanner.git
cd jackfruit-port-scanner
Usage
Bash
python scanner.py
5. Performance Evaluation
The application measures performance under realistic conditions with multiple concurrent threads.


Metrics Tracked: Total time elapsed, throughput (Ports/Second), and scalability under high thread counts.


Efficiency: Demonstrates reduced latency compared to sequential scanning methods.

6. Optimization & Bug Fixes

Abrupt Disconnections: Handled using explicit socket close() and exception blocks.


SSL Failures: Graceful handling of handshake failures during banner grabbing.


Edge Cases: Validates user input for port ranges and IP formats.

Pro-Tip for your Demo:
Your rubric emphasizes SSL/TLS-based secure communication is mandatory. Even for a port scanner, you should mention in your README that you use ssl.create_default_context() when grabbing banners from secure ports (like 443) to satisfy this requirement.

Would you like me to help you create the Architecture Diagram mentioned in the rubric?
