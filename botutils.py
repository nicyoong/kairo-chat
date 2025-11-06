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