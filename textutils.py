import re
from collections import Counter

def text_to_vector(text):
    """Fast, lightweight vectorizer (token frequency)."""
    words = re.findall(r"\b\w+\b", text.lower())
    counts = Counter(words)
    total = sum(counts.values())
    return {w: c / total for w, c in counts.items()}

def is_mostly_chinese(text, threshold=0.8):
    chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return (chinese_chars / len(text)) >= threshold if len(text) > 0 else False

def truncate_chinese_text(text: str, limit: int = 1000) -> str:
    """
    Truncate text to <= limit characters, stopping at the last Chinese punctuation mark
    before the limit for smoothness.
    """
    if len(text) <= limit:
        return text

    truncated = text[:limit]
    punctuation_marks = ["。", "！", "？", "；", "，"]
    last_punct = max((truncated.rfind(p) for p in punctuation_marks), default=-1)
    if last_punct != -1:
        truncated = truncated[: last_punct + 1]
    return truncated