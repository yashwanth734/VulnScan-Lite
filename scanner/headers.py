import requests

SECURITY_HEADERS = [
  "Content-Security-Policy",
  "X-Frame-Options",
  "Strict-Transport-Security",
  "X-Content-Type-Options",
  "Referrer-Policy"
]

def check_headers(url, timeout=10):
    try:
        user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=user_agent, timeout=timeout, allow_redirects=True)
        # requests.headers is a CaseInsensitiveDict
        response_headers = r.headers
    except Exception as e:
        return {"ok": False, "error": str(e)}

    checks = {}
    score_delta = 0
    for h in SECURITY_HEADERS:
        present = h in response_headers
        checks[h] = {"present": present, "value": response_headers.get(h)}
        score_delta += 10 if present else -10

    # Convert to standard dict for JSON serialization
    headers_dict = {k: v for k, v in response_headers.items()}
    return {"ok": True, "headers": headers_dict, "checks": checks, "score_delta": score_delta}
