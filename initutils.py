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

    for channel in all_text_like:
        try:
            # Skip locked or archived threads
            if isinstance(channel, discord.Thread) and (
                channel.archived or not channel.permissions_for(guild.me).send_messages
            ):
                print(f"Skipping archived or inaccessible thread: #{channel.name}")
                continue
            if not channel.permissions_for(guild.me).send_messages:
                print(f"Skipping #{channel.name}: no permission to send messages.")
                continue
            is_nsfw = getattr(channel, "nsfw", False)
            if is_nsfw:
                print(f"Skipping NSFW channel: #{channel.name}")
                continue
            await initialize_channel_context(bot, chatbot, guild, channel, displayname)
        except Exception as e:
            print(f"Error initializing {channel.name}: {e}")

async def send_split_response(bot, chatbot, dm, user_id, response_text, displayname):
    if chatbot.user_contexts.get(str(user_id), {}).get("is_short_reply", False):
        sentences = [response_text]
    else:
        sentences = textutils.smart_split(response_text)

