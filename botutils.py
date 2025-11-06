import asyncio
import heapq
import os
import random
import time
from datetime import datetime

import discord
import yaml
from dotenv import load_dotenv

load_dotenv()

URGENT_TRIGGER = os.getenv("URGENT_TRIGGER")
URGENT_TRIGGER1H = os.getenv("URGENT_TRIGGER1H")
QUIET_HOURS = [
    {"days": range(7), "start": (3, 0), "end": (6, 0)},
    {"days": range(0, 5), "start": (9, 0), "end": (12, 0)},
    {"days": [6], "start": (10, 0), "end": (14, 0)},
]

def ensure_config_exists(config_path="config.yml"):
    """Check for a config.yml file and generate it with defaults if missing."""
    default_config = {
        "serious_channels": [],
        "short_reply_channels": [],
        "manual_channels": [],
        "short_reply_guilds": [],
        "short_reply_users": [],
        "allowed_guilds": [],
        "allowed_users": []
    }

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        print(f"[CONFIG] Created default {config_path}")
    else:
        with open(config_path, "r") as f:
            try:
                config_data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                print(f"[CONFIG ERROR] Invalid YAML format: {e}")
                config_data = {}

        updated = False
        for key in default_config:
            if key not in config_data:
                config_data[key] = default_config[key]
                updated = True

        if updated:
            with open(config_path, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            print(f"[CONFIG] Updated {config_path} with missing default keys.")
        else:
            print(f"[CONFIG] {config_path} already exists and is complete.")