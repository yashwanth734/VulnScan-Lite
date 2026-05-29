import requests

# List of important security headers to check
SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "Strict-Transport-Security"
]

def check_headers(url):
    """
    Fetches the HTTP headers from the given URL and checks
    for the presence of key security headers.
    Returns a dictionary with score and details.
    """
    try:
        r = requests.get(url, timeout=10)
        headers = r.headers
        score = 0
        results = {}

        for h in SECURITY_HEADERS:
            if h in headers:
                score += 10
                results[h] = "Present"
            else:
                score -= 10
                results[h] = "Missing"

        return {"score": score, "details": results}

    except Exception as e:
        # If something goes wrong (like invalid URL or timeout)
        return {"score": 0, "error": str(e)}
