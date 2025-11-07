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

def load_nsfw_filters():
    """Initialize NSFW word patterns and responses from environment."""
    nsfw_env = os.getenv("NSFW_WORDS", "")
    nsfw_words = [w.strip().lower() for w in nsfw_env.split(",") if w.strip()]
    patterns = []
    for word in nsfw_words:
        # match full words only
        pattern = rf"\b{re.escape(word)}\b"
        patterns.append(re.compile(pattern, re.IGNORECASE))
    responses = [
        "That’s not appropriate. I won’t continue with that topic.",
        "I can’t discuss sexual or explicit content.",
        "Please keep the conversation respectful and safe for work.",
        "That crosses a line I will not entertain.",
    ]
    return {
        "patterns": patterns,
        "responses": responses,
    }

def contains_match(text: str, patterns: list[re.Pattern]) -> bool:
    """Check if text matches any compiled pattern."""
    text = text.lower()
    return any(p.search(text) for p in patterns)