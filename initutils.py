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

async def handle_unread_channel_message(bot, chatbot, guild, channel, messages, displayname):
    """If the last message in a guild text channel is unread (user -> before startup), reply naturally."""
    if hasattr(chatbot, "manual_channel_ids"):
        if str(channel.id) in chatbot.manual_channel_ids:
            print(f"[MANUAL ONLY] Skipping unread reply in #{channel.name} ({channel.id})")
            return
    if not messages or messages[-1]["role"] != "user":
        return
    if messages[-1].get("timestamp", 0) > bot.startup_time:
        return
    last_msg = messages[-1]
    author_id = last_msg["author_id"]
    author_name = last_msg["author_name"]
    user_text = last_msg["content"]
    print(f"Detected unread message in #{channel.name} from {author_name}, replying now...")


async def send_split_response(bot, chatbot, dm, user_id, response_text, displayname):
    if chatbot.user_contexts.get(str(user_id), {}).get("is_short_reply", False):
        sentences = [response_text]
    else:
        sentences = textutils.smart_split(response_text)
    total_tokens = sum(chatbot._calculate_tokens(s) for s in sentences)
    total_chars = sum(len(s) for s in sentences)
    print(f"Total tokens in this response: {total_tokens}")
    print(f"Total characters in this response: {total_chars}")
    # input_tokens = chatbot.user_contexts[str(user_id)].get("last_input_tokens", 0)
    # total_cost = costutils.log_gemini_cost(
    #     chatbot, str(user_id), input_tokens, total_tokens
    # )
    for sentence in sentences:
        if not sentence.strip():
            continue
        sentence = textutils.clean_sentence(sentence)
        tokens = chatbot._calculate_tokens(sentence)
        delay = chatbot._calculate_typing_delay(sentence)
        print(f"Sending sentence ({tokens} tokens) after {delay:.1f}s delay")
        await asyncio.sleep(delay)
        bot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chatbot.user_loggers[str(user_id)].info(
            f"[{displayname.upper()} {user_id} @ {bot_time}] {sentence}"
        )
        await dm.send(sentence.strip())
        chatbot.user_contexts[str(user_id)]["last_bot_reply"] = time.time()
