import json
import os


def load_character_profile(profile_name):
    """
    Loads a character profile JSON file and returns it as a Python dict.
    Example: load_character_profile("lee_pei_ying")
    """
    filename = f"{profile_name}.json"
    base_dir = os.path.dirname(__file__)
    filepath = os.path.join(base_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Character JSON file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data