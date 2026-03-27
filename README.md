# 🔒 Custom Port Scanner with Service Detection
**Socket Programming – Jackfruit Mini Project**

## 📋 Table of Contents
1. [Problem Definition](#1-problem-definition)
2. [Architecture](#2-architecture)
3. [Core Implementation](#3-core-implementation)
4. [Features](#4-features)
5. [Performance Evaluation](#5-performance-evaluation)
6. [Optimization & Bug Fixes](#6-optimization--bug-fixes)
7. [Setup Instructions](#setup-instructions)
8. [Usage Guide](#usage-guide)
9. [Technical Documentation](#technical-documentation)
10. [Evaluation Criteria Mapping](#evaluation-criteria-mapping)

---

## 1. Problem Definition

### Objective
Design and implement a **secure, high-performance network scanner** using low-level socket programming that demonstrates:

✅ **Explicit Socket Operations**
- Manual socket creation, binding, and connection management
- Direct TCP/UDP handshake implementation
- Explicit resource cleanup and error handling

✅ **Multi-Threaded Concurrency**
- Support for 100+ concurrent worker threads
- ThreadPoolExecutor-based thread pool management
- Efficient connection pooling

✅ **Service Identification**
- Banner grabbing to identify running services (FTP, SSH, HTTP, etc.)
- Protocol-specific payload handling

✅ **SSL/TLS Secure Communication (Mandatory)**
- Implements `ssl.create_default_context()` for secure connections
- TLS wrapping for HTTPS service detection (port 443)
- Secure data exchange for all communications

---

## 2. Architecture

### System Design
```plaintext
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│           (CLI: target IP, port range, options)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  DNS Resolution Module                       │
│        Resolves hostname to IP addresses using socket        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Concurrency Engine (ThreadPool)                 │
│          ThreadPoolExecutor: 100+ worker threads             │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴──────────────────┐
        │                                │
   ┌────▼─────────┐             ┌────────▼──────┐
   │ TCP Probing  │             │ UDP Probing    │
   │   Module     │             │   Module       │
   └────┬─────────┘             └────────┬───────┘
        │                                │
        └─────────────┬──────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│         Port Status Detection (Open/Closed/Filtered)         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│        Banner Grabbing & Service Detection                   │
│   SSL/TLS Connection: ssl.create_default_context()           │
│   Service Identification via protocol handshakes             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Results & Reporting Module                      │
│     (Console output, JSON export, detailed logging)          │
└─────────────────────────────────────────────────────────────┘
