# Predefined categories and their associated keywords.
# In a real system these might come from a config file or database table,
# but for the MVP, a simple dictionary keeps things easy to read and extend.
CATEGORY_KEYWORDS = {
    "abusive": ["idiot", "stupid", "dumb", "moron", "loser", "ugly",
        "pathetic", "worthless", "trash", "garbage", "disgusting",
        "shut up", "clown", "fool", "jerk", "scum"],
    "hate_speech": ["hate you", "hate them", "racist", "sexist", "bigot",
        "go back to your country", "you people", "inferior race",
        "subhuman", "nazi"],
    "violence": ["kill", "attack", "shoot", "bomb", "murder", "stab",
        "beat you up", "hurt you", "destroy you", "burn it down",
        "gun down", "assault"],
    "spam": ["act now", "limited time", "limited offer", "offer expires","hurry up", "don't miss out", "last chance", "expires soon"],
}


def moderate_text(text: str) -> dict:
    """
    Analyze the given text against predefined keyword categories.
    Returns a dict with is_flagged, category, and confidence.
    """
    text_lower = text.lower()

    best_category = "clean"
    best_match_count = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        match_count = sum(1 for keyword in keywords if keyword in text_lower)

        if match_count > best_match_count:
            best_match_count = match_count
            best_category = category

    is_flagged = best_match_count > 0

    # Simple confidence formula: each matched keyword adds 0.3,
    # capped at 0.95 so we never claim full certainty.
    confidence = min(0.95, 0.5 + (best_match_count * 0.15)) if is_flagged else 0.10

    return {
        "is_flagged": is_flagged,
        "category": best_category,
        "confidence": round(confidence, 2),
    }