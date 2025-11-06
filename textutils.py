import re
from collections import Counter

def text_to_vector(text):
    """Fast, lightweight vectorizer (token frequency)."""
    words = re.findall(r"\b\w+\b", text.lower())
    counts = Counter(words)
    total = sum(counts.values())
    return {w: c / total for w, c in counts.items()}