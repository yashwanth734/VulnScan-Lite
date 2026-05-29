import requests
from bs4 import BeautifulSoup

def detect_cms(url, timeout=10):
    try:
        user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=user_agent, timeout=timeout)
        headers = r.headers
        html = r.text
    except Exception as e:
        return {"ok": False, "error": str(e)}

    generator = None
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", attrs={"name":"generator"})
    if meta and meta.get("content"):
        generator = meta["content"]

    xpb = headers.get("X-Powered-By")
    cms = {"generator": generator, "x_powered_by": xpb}
    issues = []
    score_delta = 0
    if generator and "WordPress" in generator:
        # naive version parse
        if "5.0" in generator or "4." in generator:
            issues.append("Outdated WordPress detected")
            score_delta -= 20
    
    if generator and "Joomla" in generator:
        if "1.5" in generator or "2." in generator or "3." in generator:
            issues.append("Outdated Joomla detected")
            score_delta -= 20
            
    if xpb and "Drupal" in xpb:
        if "7" in xpb or "8" in xpb:
            issues.append("Outdated Drupal detected")
            score_delta -= 20
    return {"ok": True, "cms": cms, "issues": issues, "score_delta": score_delta}
