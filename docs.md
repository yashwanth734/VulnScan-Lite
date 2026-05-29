# VulnScan Lite - Scanning Logic Documentation

VulnScan Lite is designed to perform safe, passive security analysis on target websites. Rather than executing intrusive payloads, the scanner identifies common misconfigurations by analyzing HTTP responses, certificates, and HTML metadata.

## 1. Header Analysis (`scanner/headers.py`)
The header module inspects the HTTP response headers for missing or misconfigured security controls.

- **Content-Security-Policy (CSP)**: We check for the presence of the `Content-Security-Policy` header. If missing, it indicates the site is vulnerable to Cross-Site Scripting (XSS) and data injection attacks.
- **X-Frame-Options**: We look for `X-Frame-Options` set to `DENY` or `SAMEORIGIN`. If missing, the site is vulnerable to Clickjacking attacks where an attacker embeds the site in an invisible iframe.
- **Strict-Transport-Security (HSTS)**: We check for `Strict-Transport-Security`. If missing, the site does not enforce HTTPS connections, making users vulnerable to Man-in-the-Middle (MitM) downgrade attacks.
- **Grading logic**: Each present header adds 10 points to the total score; each missing header deducts 10 points.

## 2. SSL/TLS Inspection (`scanner/ssl_check.py`)
This module connects to the target via HTTPS using Python's native `ssl` socket wrapper.

- **Certificate Validity**: We extract the `notAfter` field from the certificate to ensure it hasn't expired. An expired certificate results in browser warnings and compromised trust.
- **Cipher Strength**: The module inspects the negotiated cipher suite. While it doesn't aggressively test all ciphers, it ensures the basic connection succeeds under the default secure context (which disables known weak protocols like SSLv2/v3).

## 3. CMS Detection (`scanner/cms_detect.py`)
The CMS detection module uses `requests` and `BeautifulSoup` to parse the HTML DOM and HTTP headers for version disclosures.

- **Meta Generator Tags**: We search the HTML for `<meta name="generator" content="...">`. If we detect strings matching `WordPress`, `Joomla`, or `Drupal`, we parse the version number.
- **Outdated Version Checks**: We cross-reference the detected version against a hardcoded list of major versions. If the version is significantly behind the current stable release train, we flag it as an "Outdated CMS".
- **HTTP Headers**: We also inspect the `X-Powered-By` header (e.g., `PHP/5.6.40`) to detect outdated underlying technologies.

## Why Passive Scanning?
By relying entirely on reading standard web responses (HTTP headers, public certificates, and DOM tags), VulnScan Lite operates legally and safely. It does not send malformed requests, fuzz inputs, or attempt authentication bypass, making it suitable as a preliminary health check rather than a penetration testing framework.
