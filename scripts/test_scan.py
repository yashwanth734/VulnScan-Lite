import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scanner import check_headers, check_ssl, detect_cms, utils
u = utils.normalize_url("example.com")
h = check_headers(u)
s = check_ssl(u)
c = detect_cms(u)
score = 50 + h.get("score_delta",0) + s.get("score_delta",0) + c.get("score_delta",0)
print({"url":u, "score":score, "grade": utils.score_to_grade(score), "parts": {"headers":h, "ssl":s, "cms":c}})
