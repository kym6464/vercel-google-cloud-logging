import json
import os
import hmac
import hashlib

import functions_framework

from transform import transform


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

    # NOTE when verifying URL ownership, Vercel does not send the correct
    # `content-type` header so we can't use `req.is_json`.
    body_json = req.get_json(force=True, silent=True)
    if body_json is None:
        message = "Expected request body to be JSON"
        log(
            message=message,
            request_body=req.get_data(as_text=True),
            content_type=req.headers.get("content-type"),
        )
        return {"message": "Expected request body to be JSON"}, 400

    # NOTE when verifying URL ownership, Vercel sends an empty body without the
    # `x-vercel-signature` signature.
    if body_json == {}:
        VERCEL_VERIFICATION_KEY = os.environ.get("VERCEL_VERIFICATION_KEY")
        if VERCEL_VERIFICATION_KEY in [None, "TODO"]:
            log("VERCEL_VERIFICATION_KEY is not set", severity="ERROR")
        return (
            {"message": "Verifying URL ownership"},
            200,
            {"x-vercel-verify": VERCEL_VERIFICATION_KEY},
        )

    # https://vercel.com/docs/rest-api#securing-your-log-drains
    received_signature = req.headers.get("x-vercel-signature")
    if not received_signature:
        return {"message": "Missing signature"}, 401
    body_text = req.get_data(as_text=True)
    expected_signature = hmac.new(
        SECRET_KEY.encode(), body_text.encode(), hashlib.sha1
    ).hexdigest()
    if not hmac.compare_digest(received_signature, expected_signature):
        log(
            message="Invalid signature",
            request_body=body_text,
            received_signature=received_signature,
            severity="WARNING",
        )
        return {"message": "Invalid signature"}, 403

    if not isinstance(body_json, list):
        message = "Expected request body to be an object array"
        log(message, severity="ERROR")
        return {"message": message}, 400

    for vercel_log in body_json:
        log_entry = transform(vercel_log)
        print(json.dumps(log_entry))

    return {"ok": True}
