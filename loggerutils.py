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

    def __init__(
        self,
        # max calls per day is number of api keys * 1000
        max_calls_per_day: int = 5 * 1000,
        warning_threshold_ratio: float = 0.9,
        subfolder: str = "gemini",
    ):
        self.max_calls_per_day = max_calls_per_day
        self.warning_threshold = int(max_calls_per_day * warning_threshold_ratio)
        self.log_dir = os.path.join("logs", subfolder)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "call_log.csv")

    def _read_timestamps(self):
        """Read all timestamps (as float epoch times) from the CSV file."""
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            return [float(row[0]) for row in reader if row]

    