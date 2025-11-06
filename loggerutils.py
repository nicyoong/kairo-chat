import bisect
import builtins
import csv
import io
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import textutils

class GeminiLogTracker:
    """
    Tracks API call timestamps in logs/gemini/call_log.csv.
    Maintains a rolling 24-hour window and warns when usage nears capacity.
    """