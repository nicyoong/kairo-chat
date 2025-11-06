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