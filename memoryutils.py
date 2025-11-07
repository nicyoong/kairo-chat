import asyncio
import math
import os
import random
import time
from datetime import datetime

import loggerutils
import textutils


async def memory_job(context):
    await asyncio.get_event_loop().run_in_executor(
        None, loggerutils.process_chat_memories, context.bot_data["chatbot"]
    )

async def realistic_friend_delay(user_context):
    """
    Simulate human-like delay before replying.
    """
    now = time.time()
    last_user = user_context.get("last_activity", 0)
    last_bot = user_context.get("last_bot_reply", 0)
    last_event = max(last_user, last_bot)
    minutes_since_last = (now - last_event) / 60

    # Choose delay profile based on recency of chat
    if minutes_since_last <= 5:
        # Active conversation
        roll = random.random()
        if roll < 0.7:
            delay = 0
        else:
            delay = random.uniform(60, 180)  # 1–3 minutes
    else:
        # Idle or casual gap
        roll = random.random()
        if roll < 0.3:
            delay = 0
        else:
            delay = random.uniform(60, 600)  # 1–10 minutes

    if delay > 0:
        print(f"Waiting {delay/60:.1f} minutes before responding...")
        await asyncio.sleep(delay)

async def store_memory_vector(chatbot, location_key, message_text):
    """Store a single message as a vectorized memory for a given context (DM, channel, or group DM)."""
    try:
        # Create folder for this context
        logs_dir = os.path.join("logs", str(location_key))
        os.makedirs(logs_dir, exist_ok=True)
        memory_file = os.path.join(logs_dir, "memories.log")

        # Compute normalized word-frequency vector
        vec = textutils.text_to_vector(message_text)
        vec_str = ",".join(f"{hash(k)%100000}:{v:.4f}" for k, v in vec.items())

        # Append to memory log
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}]|{vec_str}|{message_text.strip()}\n")

    except Exception as e:
        print(f"[{location_key}] Error writing memory vector: {e}")

def _cosine_similarity(self, vec1, vec2):
    """Compute cosine similarity between two small dict vectors."""
    common = set(vec1.keys()) & set(vec2.keys())
    num = sum(vec1[w] * vec2[w] for w in common)
    den1 = math.sqrt(sum(v * v for v in vec1.values()))
    den2 = math.sqrt(sum(v * v for v in vec2.values()))
    return num / (den1 * den2) if den1 and den2 else 0.0

def _vector_from_line(self, vec_str):
    """Convert 'hash:weight' CSV string back to dict."""
    v = {}
    for pair in vec_str.split(","):
        if ":" in pair:
            h, w = pair.split(":")
            try:
                v[int(h)] = float(w)
            except ValueError:
                pass
    return v

def recall_relevant_memories(self, user_input, top_k=5):
    mem_file = "logs/memories.log"
    if not os.path.exists(mem_file):
        return []
    input_vec = textutils.text_to_vector(user_input)
    memories = []
    with open(mem_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                ts, vec_str, summary = line.strip().split("|", 2)
                mem_vec = _vector_from_line(vec_str)
                sim = _cosine_similarity(input_vec, mem_vec)
                memories.append((sim, ts, summary))
            except ValueError:
                continue
    # Sort by similarity descending
    memories.sort(key=lambda x: x[0], reverse=True)
    top = [f"[{t}] {s}" for _, t, s in memories[:top_k] if _ > 0.01]
    return top
