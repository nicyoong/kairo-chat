import asyncio
import os
import random
import time
from datetime import datetime, timedelta, timezone

import selfcord as discord
from dotenv import load_dotenv
from tqdm import tqdm

import botutils
import loggerutils
import textutils
import costutils

load_dotenv()


async def initialize_guild_channels(bot, chatbot, guild, displayname):
    # Include both normal text channels and threads
    all_text_like = list(guild.text_channels) + list(guild.threads)
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Fetching {len(all_text_like)} channels/threads for guild: {guild.name}"
    )

