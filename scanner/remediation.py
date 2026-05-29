REMEDIATION_TIPS = {
    "Missing header: Content-Security-Policy": "Add 'Content-Security-Policy' to your web server response headers. Example (Nginx): add_header Content-Security-Policy \"default-src 'self'\";",
    "Missing header: X-Frame-Options": "Add 'X-Frame-Options: DENY' or 'SAMEORIGIN' to prevent Clickjacking.",
    "Missing header: Strict-Transport-Security": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' to enforce HTTPS.",
    "Missing header: X-Content-Type-Options": "Add 'X-Content-Type-Options: nosniff' to prevent MIME-sniffing.",
    "Missing header: Referrer-Policy": "Add 'Referrer-Policy: strict-origin-when-cross-origin' to control referrer information.",
    "SSL Certificate Invalid or Expired": "Renew your SSL certificate using a provider like Let's Encrypt.",
    "Outdated WordPress detected": "Update your WordPress installation to the latest stable version.",
    "Outdated Joomla detected": "Update your Joomla installation to the latest stable version.",
    "Outdated Drupal detected": "Update your Drupal installation to the latest stable version.",
    "Weak SSL/TLS Cipher Suite detected": "Configure your web server to use strong cipher suites (e.g., ECDHE-ECDSA-AES128-GCM-SHA256) and disable outdated protocols like SSLv2, SSLv3, TLSv1.0, and TLSv1.1. Example (Nginx): ssl_protocols TLSv1.2 TLSv1.3;",
    "SSL check failed": "Verify your domain is configured to serve HTTPS connections on port 443 with a valid certificate."
}

def get_remediation_tips(issues):
    tips = []
    for issue in issues:
        found = False
        for key, tip in REMEDIATION_TIPS.items():
            if key in issue:
                tips.append({"issue": issue, "tip": tip})
                found = True
                break
        if not found:
            tips.append({"issue": issue, "tip": "Review server configuration or contact your hosting provider."})
    return tips
