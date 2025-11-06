import asyncio
import os
import random
import time
from datetime import datetime

import discord
import yaml
from dotenv import load_dotenv
from discord import commands, tasks


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