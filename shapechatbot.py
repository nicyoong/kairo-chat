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