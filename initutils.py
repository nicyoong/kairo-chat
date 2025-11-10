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