import asyncio
import os
import random
import time
from datetime import datetime

import discord
import yaml
from dotenv import load_dotenv
from discord import commands, tasks

import botutils

load_dotenv()
typing_lock = asyncio.Lock()
urgent_queue = []
URGENT_TRIGGER = botutils.URGENT_TRIGGER
URGENT_TRIGGER1H = botutils.URGENT_TRIGGER1H
URGENT_RESPONSES = [
    "I’m here, tell me what’s going on.",
    "Hey, I’m here, what happened?",
    "I’m here now. What’s going on?",
    "I’m listening. What’s wrong?",
    "Hey, I’m here. You okay?",
]
URGENT_RESPONSES_1H = [
    "Of course, what’s up?",
    "Sure, what’s going on?",
    "Yeah, I’m here, what’s up?",
    "Okay, what’s happening?",
    "Alright, what’s up?",
]
USER_REMINDERS_ENABLED = {}
QUIET_HOURS = botutils.QUIET_HOURS
display_name = "Kairo"
profile_name = "kairo"

def main():
    botutils.ensure_config_exists()

if __name__ == "__main__":
    main()