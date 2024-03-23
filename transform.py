import copy
import json
from functools import reduce


def get(dictionary: dict, path: str, default=None):
    return reduce(
        lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
        path.split("."),
        dictionary,
    )


def to_timestamp(milliseconds: int):
    "https://cloud.google.com/logging/docs/agent/logging/configuration#timestamp-processing"
    return {"seconds": milliseconds // 1000, "nanos": (milliseconds % 1000) * 1000000}


def to_severity(level: str):
    "https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity"
    if level == "error":
        return "ERROR"
    if level == "warning":
        return "WARNING"
    if level == "info":
        return "INFO"

    message = f"Unrecognized level '{level}' received from Vercel"
    print(json.dumps({"message": message, "severity": "WARNING"}))
    return "INFO"


def transform(vercel_log: dict, *, project: str, inplace=False) -> dict:
    log_entry = vercel_log if inplace else copy.deepcopy(vercel_log)
    log_entry["logging.googleapis.com/trace"] = (
        f"projects/{project}/traces/{vercel_log['requestId']}"
    )
    log_entry["severity"] = to_severity(log_entry.pop("level", None))
    log_entry["timestamp"] = to_timestamp(vercel_log["timestamp"])
    proxy = vercel_log.get("proxy", {})

    user_agent: str | None = None
    user_agents = proxy.get("userAgent")
    if user_agents and isinstance(user_agents, list):
        user_agent = user_agents[0]

    is_cache_hit = False
    if proxy.get("vercelCache") is True:
        is_cache_hit = True

    log_entry["httpRequest"] = {
        "requestMethod": proxy.get("method"),
        "requestUrl": f"{proxy.get('scheme')}://{proxy.get('host')}{proxy.get('path')}",
        "status": vercel_log.get("statusCode"),
        "userAgent": user_agent,
        "remoteIp": proxy.get("clientIp"),
        "referer": proxy.get("referer"),
        "cacheHit": is_cache_hit,
    }

    return log_entry
