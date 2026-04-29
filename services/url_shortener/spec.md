## Problem Statement

This project is inspired by classic URL shortener system design problems commonly discussed in system design education materials.

The goal is to design a scalable URL shortening service with the following requirements:

### Functional Requirements
- Shorten long URLs into compact aliases
- Redirect shortened URLs to original destinations
- Track basic usage analytics (click counts)

### Non-Functional Requirements
- Low-latency redirection (read-heavy system)
- Scalable to high traffic workloads
- Support long-term data retention
- Rate Limiting: Prevent malicious mass generation of short URLs from overwhelming the database.

### Back-of-the-envelope estimation
- 100M DAU
- Read/Write Ratio= 100:1
- Data retention for 3 years


### Reference
Inspired by: https://systemdesignschool.io/problems/url-shortener