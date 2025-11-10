import asyncio
import os
import random
import time
from datetime import datetime

import discord
import yaml
from dotenv import load_dotenv
from discord.ext import commands, tasks

import botutils
import initutils
import shapechatbot

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
    with open("config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    chatbot = shapechatbot.ShapeChatBot(profile_name=profile_name)

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    bot.chatbot = chatbot

    async def handle_reminder_toggle(bot, message):
        """Handles per-user natural-language toggle for reminder system with typing simulation."""
        user_id = message.author.id
        content_lower = message.content.strip().lower()
        enable_trigger = "you can start reminding me again"
        disable_trigger = "you can stop reminding me for now"
        USER_REMINDERS_ENABLED.setdefault(user_id, False)
        chatbot = bot.chatbot
        if enable_trigger in content_lower:
            if not USER_REMINDERS_ENABLED[user_id]:
                USER_REMINDERS_ENABLED[user_id] = True
                response_text = "Alright, I’ll start keeping an eye on reminders again."
            else:
                response_text = "I’m already keeping track, don’t worry."
        elif disable_trigger in content_lower:
            if USER_REMINDERS_ENABLED[user_id]:
                USER_REMINDERS_ENABLED[user_id] = False
                response_text = "Okay, I’ll stop reminding you for now."
            else:
                response_text = "They’re already off, don’t worry."
        else:
            return False
        tokens = chatbot._calculate_tokens(response_text)
        typing_delay = chatbot._calculate_typing_delay(response_text)
        print(f"Sending toggle message ({tokens} tokens) after {typing_delay:.1f}s delay")
        typing_task = asyncio.create_task(botutils.keep_typing(message.channel))
        try:
            await asyncio.sleep(typing_delay)
            await message.channel.send(response_text.strip())
        finally:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass

        return True
    
    def print_startup_message(bot):
        init_time = datetime.fromtimestamp(bot.startup_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{init_time}] {display_name} is online as {bot.user}")

    def setup_chatbot_environment(bot):
        chatbot = bot.chatbot
        chatbot.user_loggers = {}
        chatbot.processing_queued = False
        bot.chatbot.last_activity_time = time.time()

    async def initialize_guilds(bot, displayname, config):
        """Initialize message histories for allowed guilds."""
        chatbot = bot.chatbot
        for guild_id in config.get("allowed_guilds", []):
            try:
                guild = bot.get_guild(int(guild_id))
            except ValueError:
                print(f"[CONFIG ERROR] Invalid guild ID: {guild_id}")
                continue
            if not guild:
                print(f"Skipping guild {guild_id}: not found or bot not in it.")
                continue
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Fetching channels for guild: {guild.name}")
            await initutils.initialize_guild_channels(bot, chatbot, guild, display_name)

if __name__ == "__main__":
    main()