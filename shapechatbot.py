import base64
import datetime
import math
import os
import random
import re
import time
from datetime import date, datetime
from PIL import Image

import tiktoken
import yaml
from openai import OpenAI

import textutils
from characterloader import load_character_profile
from characterprofile import CharacterProfile
from loggerutils import GeminiLogTracker
from traitgetters import attach_trait_getters
from traitrouter import _init_trait_router