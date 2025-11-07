import base64
import datetime
import math
import os
import random
import re
import time
from datetime import date, datetime
from PIL import Image

import tiktoken
import yaml
from openai import OpenAI

import textutils
from characterloader import load_character_profile
from characterprofile import CharacterProfile
from loggerutils import GeminiLogTracker
from traitgetters import attach_trait_getters
from traitrouter import _init_trait_router

@attach_trait_getters
class ShapeChatBot:
    def __init__(self, profile_name, test_mode=False):
        self.test_mode = test_mode
        if not test_mode:
            self.api_keys = [
                os.getenv("GEMINI_API_KEY1"),
            ]
            self.key_index = 0
            self.key_usage_count = 0
            self.max_uses_per_key = 1
            self.client = OpenAI(
                api_key=self.api_keys[self.key_index],
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            self.model = "gemini-2.5-flash-lite"
        else:
            self.client = None
            self.model = "test"
            print("[DEBUG] ShapeChatBot running in test_mode (no API calls).")
        profile_data = load_character_profile(profile_name)
        self.config_path = "config.yml"
        self._last_config_mtime = 0
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}
        else:
            yaml_config = {}
        self.personality_fun = profile_data.get("personality_fun", "")
        self.personality_serious = profile_data.get("personality_serious", "")
        self.system_prompt = {"role": "system", "content": self.personality_fun}
        self.serious_channel_ids = [str(c) for c in (yaml_config.get("serious_channels") or [])]
        self.error_responses = profile_data.get("error_responses", [])

        # Anti Swear Filter
        self.swear_responses = profile_data.get("swear_responses", [])
        swear_env = os.getenv("SWEAR_WORDS", "")
        self.swear_words = [w.strip().lower() for w in swear_env.split(",") if w.strip()]
        self.swear_patterns = []
        for word in self.swear_words:
            letters = list(word)
            pattern = r"[\W_]*".join(map(re.escape, letters)) + "+"
            compiled = re.compile(pattern, re.IGNORECASE)
            self.swear_patterns.append(compiled)