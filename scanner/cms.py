import requests
from bs4 import BeautifulSoup

def detect_cms(url):
    """
    Fetches the HTML content of the given URL and tries to detect
    if the site is using a CMS (like WordPress, Drupal, etc.)
    by looking at meta tags and headers.
    """
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Check meta generator tag
        gen = soup.find("meta", {"name": "generator"})
        if gen and "content" in gen.attrs:
            return gen["content"]

        # Check X-Powered-By header
        powered = r.headers.get("X-Powered-By")
        if powered:
            return powered

        return "Unknown"

    except Exception as e:
        return f"Error: {str(e)}"
 
