from scanner.headers import check_headers
from scanner.ssl_check import check_ssl
from scanner.cms import detect_cms
from scanner.scoring import calculate_score

def run_scan(url, domain):
    print("===== VulnScan Lite Report =====")
    print(f"Target: {url}\n")

    # Run modules
    headers_result = check_headers(url)
    ssl_result = check_ssl(domain)
    cms_result = detect_cms(url)

    # Combine results
    results = {
        "headers": headers_result,
        "ssl": ssl_result,
        "cms": cms_result
    }

    # Calculate score
    scorecard = calculate_score(results)

    # Print results
    print("🔒 Header Analysis:", headers_result)
    print("🔑 SSL/TLS Inspection:", ssl_result)
    print("🖥️ CMS Detection:", cms_result)
    print("\n📊 Final Score:", scorecard["score"])
    print("🏆 Grade:", scorecard["grade"])
    print("===== End of Report =====")

# Run scan
run_scan("https://example.com", "example.com")
