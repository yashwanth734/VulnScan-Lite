def normalize_url(url):
    if not url.startswith("http"):
        return "https://" + url
    return url

def score_to_grade(score):
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 40: return "D"
    return "F"
