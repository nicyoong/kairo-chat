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

import contentfilter
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

        swear_data = contentfilter.load_swear_filters()
        self.swear_patterns = swear_data["patterns"]
        self.swear_responses = profile_data.get("swear_responses", [])
        nsfw_data = contentfilter.load_nsfw_filters()
        self.nsfw_patterns = nsfw_data["patterns"]
        self.nsfw_responses = nsfw_data["responses"]
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
    
    def _enforce_rate_limit(self):
        """Ensure we don't exceed n requests per minute (per instance)"""
        now = time.time()
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]
        while len(self.request_timestamps) >= self.rate_limit:
            oldest = self.request_timestamps[0]
            required_wait = oldest + 60 - now + 0.1  # Small buffer
            if required_wait > 0:
                print(f"Rate limit exceeded. Waiting {required_wait:.1f} seconds...")
                time.sleep(required_wait)
            now = time.time()
            self.request_timestamps = [t for t in self.request_timestamps if now - t < 60]

    def _calculate_image_tokens(self, image_path: str) -> int:
        """Estimate Gemini image token cost based on image dimensions."""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            if width <= 384 and height <= 384:
                return 258
            tiles_x = math.ceil(width / 768)
            tiles_y = math.ceil(height / 768)
            total_tiles = tiles_x * tiles_y
            total_tokens = total_tiles * 258
            print(f"[TOKEN ESTIMATE] Image {width}x{height}px → {total_tiles} tiles → {total_tokens} tokens")
            return total_tokens
        except Exception as e:
            print(f"[IMAGE TOKEN ERROR] Failed to get image size: {e}")
            # Fallback to one tile if something goes wrong
            return 258
        
    def _flatten_message_content(self, content):
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        texts.append(part.get("text", ""))
                    elif part.get("type") == "image_url":
                        continue
                else:
                    texts.append(str(part))
            return "\n".join(texts)
        return str(content)
    
    def _calculate_tokens(self, text):
        """Count tokens using GPT-4's actual tokenization"""
        return len(self.encoder.encode(text))
    
    def _truncate_history(self, user_context):
        # while (len(user_context['conversation_history']) > self.max_messages or
        #        user_context['current_tokens'] > self.max_tokens):
        while user_context["current_tokens"] > self.max_tokens:
            if not user_context["conversation_history"]:
                break
            removed = user_context["conversation_history"].pop(0)
            user_context["current_tokens"] -= self._calculate_tokens(removed["content"])

    def _calculate_typing_delay(self, text):
        """Calculate delay based on token count (1.3 to 1.7 tokens/second) with min 0.5s"""
        tokens = self._calculate_tokens(text)
        tokens_per_second = random.choice([1.3, 1.4, 1.5, 1.6, 1.7])
        delay = tokens / tokens_per_second
        return round(max(delay, 0.5), 2)
    
    def get_response(self, user_id, user_input, is_reminder=False):
        # Check for direct trait-based answers first
        trait_reply = self.try_trait_based_response(user_input)
        if trait_reply:
            return trait_reply
        
        try:
            if contentfilter.contains_match(user_input, self.swear_patterns):
                print("Detected swear word, skipping LLM call.")
                return random.choice(self.swear_responses)
            if contentfilter.contains_match(user_input, self.nsfw_patterns):
                print("Detected NSFW content, skipping LLM call.")
                return random.choice(self.nsfw_responses)
            # Enforce global rate limit first
            self._enforce_rate_limit()
            self.request_timestamps.append(time.time())
            # Handle user context
            if user_id not in self.user_contexts:
                self.user_contexts[user_id] = {}
            uc = self.user_contexts.setdefault(user_id, {})
            uc.setdefault("conversation_history", [])
            uc.setdefault("current_tokens", 0)
            uc.setdefault("last_activity", time.time())
            uc.setdefault("reminder_sent", False)
            # Update activity and reset reminder flag for real user messages
            if not is_reminder:
                uc["last_activity"] = time.time()
                uc["reminder_sent"] = False
            is_short_reply = False
            if user_id in self.short_reply_user_ids:
                is_short_reply = True
            if isinstance(user_id, str) and user_id.startswith("guild_"):
                parts = user_id.split("_")
                guild_id = parts[1]
                channel_id = parts[3]
                if (
                    guild_id in self.short_reply_guild_ids
                    or channel_id in self.short_reply_channel_ids
                ):
                    is_short_reply = True
            uc["is_short_reply"] = is_short_reply
            is_chinese = textutils.is_mostly_chinese(user_input)
            if is_chinese:
                print("The user message is in Chinese.")
                if is_short_reply:
                    style_instruction = (
                        "请用一句自然的“口语化”语气来写出你的下一段回答。"
                        "你必须优先遵循这个指令。"
                    )
                else:
                    style_instruction = (
                        "请用几句自然的“口语化”语气来写出你的下一段回答。"
                        "你必须优先遵循这个指令。"
                    )
            else:
                if is_short_reply:
                    style_instruction = (
                        "Write your next response in one concise sentence, "
                        "still keeping a natural, conversational tone. "
                        "You must prioritize following that directive."
                    )
                else:
                    style_instruction = (
                        "Write your next response with a few sentences of 'speech' "
                        "in a conversational tone. You must prioritize following that directive."
                    )
            
            user_input_with_style = f"{user_input.strip()}\n\n{style_instruction}"
            uc["conversation_history"].append({"role": "user", "content": user_input_with_style})
            uc["current_tokens"] += self._calculate_tokens(user_input_with_style)