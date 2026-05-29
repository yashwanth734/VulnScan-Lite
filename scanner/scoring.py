def calculate_score(results):
    """
    Combine header score, SSL validity, and CMS detection
    into a normalized 0–100 score.
    """
    score = 50  # start baseline

    # Headers
    score += results["headers"]["score"]

    # SSL validity
    if results["ssl"].get("valid"):
        score += 20
    else:
        score -= 20

    # CMS detection (penalize outdated WordPress)
    cms = results["cms"]
    if "WordPress" in cms:
        try:
            version = float(cms.split()[1])
            if version < 5.0:
                score -= 10
        except:
            pass

    # Clamp between 0–100
    score = max(0, min(100, score))

    # Letter grade
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"

    return {"score": score, "grade": grade}
