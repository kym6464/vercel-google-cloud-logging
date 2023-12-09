import copy
from datetime import datetime, timezone


def parse_milliseconds(milliseconds: int) -> str:
    seconds = milliseconds / 1000.0
    dt = datetime.fromtimestamp(seconds, timezone.utc)
    return dt.isoformat()


def transform(vercel_log: dict) -> dict:
    log_entry = copy.deepcopy(vercel_log)
    log_entry["severity"] = "INFO"
    log_entry["timestamp"] = parse_milliseconds(vercel_log["timestamp"])
