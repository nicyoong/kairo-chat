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

    def _write_timestamps(self, timestamps):
        """Write timestamps back to the CSV file (truncate if over limit)."""
        timestamps = timestamps[-self.max_calls_per_day :]  # keep only newest
        with open(self.log_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for ts in timestamps:
                writer.writerow([f"{ts:.3f}"])

    def log_call(self):
        """
        Record a new API call timestamp.
        Remove entries older than 24 hours.
        Warn if usage exceeds the threshold.
        """
        now = time.time()
        one_day_ago = now - 24 * 3600

        timestamps = self._read_timestamps()
        timestamps = [ts for ts in timestamps if ts >= one_day_ago]
        timestamps.append(now)

        count = len(timestamps)
        self._write_timestamps(timestamps)

        # Console warnings
        if count > self.warning_threshold and count < self.max_calls_per_day:
            print(
                f"[GeminiLogTracker] Warning: {count}/{self.max_calls_per_day} "
                f"calls logged in the past 24 hours ({count/self.max_calls_per_day:.1%})."
            )
        elif count >= self.max_calls_per_day:
            print(f"[GeminiLogTracker] LIMIT REACHED: {count} calls in the last 24 hours!")

    def count(self) -> int:
        """
        Return the number of calls logged within the last 24 hours.
        """
        now = time.time()
        one_day_ago = now - 24 * 3600
        timestamps = [ts for ts in self._read_timestamps() if ts >= one_day_ago]
        return len(timestamps)
    
    def max_calls_per_minute(self) -> int:
        """
        Return the maximum number of calls that occurred within any 60-second window
        in the past 24 hours.
        """
        timestamps = self._read_timestamps()
        if not timestamps:
            return 0

        # Keep only last 24h
        now = time.time()
        one_day_ago = now - 24 * 3600
        timestamps = [ts for ts in timestamps if ts >= one_day_ago]
        timestamps.sort()

        max_in_window = 0
        window = 60  # seconds

        # Sliding window approach using bisect
        for i, ts in enumerate(timestamps):
            end_time = ts + window
            j = bisect.bisect_right(timestamps, end_time)
            count = j - i
            if count > max_in_window:
                max_in_window = count

        return max_in_window
    
def setup_console_logger(log_name: str, subfolder: str = "console"):
    """Sets up a global console logger that writes to both console and file."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    log_dir = os.path.join("logs", subfolder)
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{log_name}_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    log_path = os.path.join(log_dir, log_filename)

    logger = logging.getLogger(f"{log_name}_console")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Clean old handlers (avoid duplicates)
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    # File handler (rotating)
    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    