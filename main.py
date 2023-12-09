import json
import os
import hmac
import hashlib

import functions_framework


SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY is not set")


def log(message_or_payload: str | dict | None = None, *, severity="INFO", **kwds):
    """
    Helper to write a structured log to stdout to be picked up by the GCP logging agent

    :param message_or_payload: Text or structured log
    :param severity: https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity
    """
    log_entry = {"severity": severity}
    if isinstance(message_or_payload, str):
        log_entry["message"] = message_or_payload
    elif isinstance(message_or_payload, dict):
        log_entry.update(message_or_payload)
    if kwds:
        log_entry.update(kwds)
    print(json.dumps(log_entry))


@functions_framework.http
def on_log(req):
    """
    :param req: The request object (flask.Request)
        https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    :returns Response object using `make_response`
        https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response
    """
    if req.method != "POST":
        return {"message": f"Invalid method '{req.method}'"}, 405
    if not req.is_json:
        return {"message": "Expected application/json"}, 400

    # Verify HMAC signature
    # https://vercel.com/docs/rest-api#securing-your-log-drains
    received_signature = req.headers.get("x-vercel-signature")
    if not received_signature:
        return {"message": "Missing signature"}, 401
    request_data = req.get_data(as_text=True)
    expected_signature = hmac.new(
        SECRET_KEY.encode(), request_data.encode(), hashlib.sha1
    ).hexdigest()
    if not hmac.compare_digest(received_signature, expected_signature):
        log(
            message="Invalid signature",
            request_data=request_data,
            received_signature=received_signature,
            severity="WARNING",
        )
        return {"message": "Invalid signature"}, 403

    body = req.json
    log({"message": "Request body", "body": body})

    return ({"ok": True}, 200)


@functions_framework.http
def on_verify(req):
    VERCEL_VERIFICATION_KEY = os.environ.get("VERCEL_VERIFICATION_KEY")
    if not VERCEL_VERIFICATION_KEY:
        raise Exception("Missing VERCEL_VERIFICATION_KEY")
    return (
        {"ok": True},
        200,
        {"x-vercel-verify": VERCEL_VERIFICATION_KEY},
    )
