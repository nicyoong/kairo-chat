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

def smart_split(text):
    """Split text into natural-sounding chunks based on punctuation and newlines."""
    text = text.strip().replace("\r\n", "\n").replace("\r", "\n")

    line_blocks = [block.strip() for block in text.split("\n") if block.strip()]
    final_parts = []
    for block in line_blocks:
        sentences = re.split(r"(?<=[.!?]) +", block)
        for s in sentences:
            if not s.strip():
                continue
            parts = s.split(",")
            if len(parts) > 2:
                for i in range(0, len(parts), 2):  # group every two comma parts
                    chunk = ",".join(parts[i : i + 2]).strip()
                    if chunk:
                        final_parts.append(chunk)
            else:
                final_parts.append(s.strip())
    return final_parts

def clean_unpaired_quotes(text: str) -> str:
    """
    Remove stray or unpaired double quotes (“ or ” or ")
    that appear at the start or end of sentences.
    Keeps proper paired quotes intact.
    """
    text = text.strip()

    # Remove a leading stray quote (if not followed by another later)
    if re.match(r'^[“"]\s*\w', text) and text.count('"') % 2 != 0:
        text = re.sub(r'^[“"]\s*', "", text)

    # Remove trailing stray quotes (like ...!" or ...?" etc.)
    if text.count('"') % 2 != 0 or text.count("”") % 2 != 0:
        text = re.sub(r'["”]+(?=\s*[^\w\s]*$)', "", text)

    return text.strip()

def clean_all_quotes(text: str) -> str:
    return re.sub(r'[“”"]', "", text)