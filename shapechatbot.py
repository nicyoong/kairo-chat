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

        # Anti NSFW Filter (Hardcoded responses)
        self.nsfw_responses = [
            "That’s not appropriate. I won’t continue with that topic.",
            "I can’t discuss sexual or explicit content.",
            "Please keep the conversation respectful and safe for work.",
            "That crosses a line I will not entertain.",
        ]
        nsfw_env = os.getenv("NSFW_WORDS", "")
        self.nsfw_words = [w.strip().lower() for w in nsfw_env.split(",") if w.strip()]
        self.nsfw_patterns = []
        for word in self.nsfw_words:
            letters = list(word)
            pattern = rf"\b{re.escape(word)}\b"
            compiled = re.compile(pattern, re.IGNORECASE)
            self.nsfw_patterns.append(compiled)

        self.character_profile = CharacterProfile(profile_data)
        _init_trait_router(self)

        self.max_messages = 50
        self.max_tokens = 10000
        self.user_contexts = {}
        self.last_active_user = None

        # Rate limiting configuration
        self.rate_limit = 2  # 2 request per minutes
        self.request_timestamps = []
        self.gemini_log_tracker = GeminiLogTracker(
            max_calls_per_day=(1000), warning_threshold_ratio=0.9
        )
        self.encoder = tiktoken.get_encoding("cl100k_base")

        self.short_reply_channel_ids = [
            str(c) for c in (yaml_config.get("short_reply_channels") or [])
        ]
        self.manual_channel_ids = [str(c) for c in (yaml_config.get("manual_channels") or [])]
        self.short_reply_guild_ids = [str(c) for c in (yaml_config.get("short_reply_guilds") or [])]
        self.short_reply_user_ids = [str(c) for c in (yaml_config.get("short_reply_users") or [])]
        self._last_config_mtime = os.path.getmtime(self.config_path)
        self.is_currently_driving = False

    def reload_config(self):
        """Reload config.yml periodically."""
        config_path = "config.yml"
        try:
            if not os.path.exists(config_path):
                return
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > getattr(self, "_last_config_mtime", 0):
                print("[CONFIG] Detected config.yml change — reloading...")
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        yaml_config = yaml.safe_load(f) or {}
                    self.serious_channel_ids = [
                        str(c) for c in (yaml_config.get("serious_channels") or [])
                    ]
                    self.short_reply_channel_ids = [
                        str(c) for c in (yaml_config.get("short_reply_channels") or [])
                    ]
                    self.manual_channel_ids = [
                        str(c) for c in (yaml_config.get("manual_channels") or [])
                    ]
                    self.short_reply_guild_ids = [
                        str(c) for c in (yaml_config.get("short_reply_guilds") or [])
                    ]
                    self.short_reply_user_ids = [
                        str(c) for c in (yaml_config.get("short_reply_users") or [])
                    ]
                    self._last_config_mtime = current_mtime
                    print("[CONFIG] Reloaded config.yml successfully.")
                except Exception as e:
                    print(f"[CONFIG ERROR] Failed to reload config.yml: {e}")
        except Exception as e:
            print(f"[CONFIG ERROR] Could not check config file: {e}")

    def _parse_iso_date(self, s: str):
        """
        Parse 'YYYY-MM-DD' into a date object. Returns None if invalid.
        """
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
        
    def _compute_age_from_birthday(self, bday_str: str, today: date | None = None):
        """
        Compute age from ISO birthday. Falls back to the stored 'age' if birthday is missing/invalid.
        """
        if today is None:
            today = datetime.date.today()
        bday = self._parse_iso_date(bday_str) if bday_str else None
        if not bday:
            # fallback to static value if available
            return self.get_trait("age", None)
        years = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
        return years
    
    def try_trait_based_response(self, user_input: str):
        """Check if user_input matches a known question and return a natural answer."""
        text = user_input.lower().strip()
        text = text.replace("’", "'").replace("‘", "'")

        for entry in self.trait_router:
            if any(p in text for p in entry["patterns"]):
                getter = entry["getter"]
                value = getter() if callable(getter) else None
                if not value:
                    return None
                template = random.choice(entry["responses"])
                return template.format(value)

        return None
    
    def _rotate_api_key(self):
        """Rotate API key after every N requests."""
        self.key_usage_count += 1
        if self.key_usage_count >= self.max_uses_per_key:
            self.key_usage_count = 0
            self.key_index = (self.key_index + 1) % len(self.api_keys)
            new_key = self.api_keys[self.key_index]
            self.client = OpenAI(
                api_key=new_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            print(f"Switched to API key {self.key_index + 1}")