# this is a small logger to make debugging easier
from datetime import datetime
import sys

GRAY = "\033[90m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def _log(level: str, color: str, *args, **kwargs):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    message = sep.join(str(arg) for arg in args)
    print(f"{GRAY}{timestamp}{RESET} | {color}{level:<7}{RESET} | {message}", end=end)

def log_err(*args, **kwargs):
    _log("ERROR", RED, *args, **kwargs)

def log_ok(*args, **kwargs):
    _log("SUCCESS", GREEN, *args, **kwargs)

def log_warn(*args, **kwargs):
    _log("WARNING", YELLOW, *args, **kwargs)

def log_info(*args, **kwargs):
    _log("INFO", BLUE, *args, **kwargs)
