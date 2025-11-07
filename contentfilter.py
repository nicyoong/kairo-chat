import os
import re

def load_swear_filters():
    """Initialize swear word patterns and responses from environment."""
    swear_env = os.getenv("SWEAR_WORDS", "")
    swear_words = [w.strip().lower() for w in swear_env.split(",") if w.strip()]
    patterns = []
    for word in swear_words:
        letters = list(word)
        # allow punctuation or underscores between letters
        pattern = r"[\W_]*".join(map(re.escape, letters)) + "+"
        patterns.append(re.compile(pattern, re.IGNORECASE))
    return {
        "patterns": patterns,
        "responses": []
    }