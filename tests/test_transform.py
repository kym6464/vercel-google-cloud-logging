from transform import transform

project = "test-project"

vercel_log = {
    "id": "1669118385998052846361484418",
    "message": "SAMPLE MESSAGE: START RequestId: xxxxxxxxxxxxxxxxx Version: $LATEST\nEND RequestId: xxxxxxxxxxxxxxxxx\nREPORT RequestId: xxxxxxxxxxxxxxxxx\tDuration: 1472.20 ms\tBilled Duration: 1473 ms\tMemory Size: 1024 MB\tMax Memory Used: 147 MB\t\n",
    "timestamp": 1702129361444,
    "requestId": "cdg1::iad1::xxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxx",
    "statusCode": 200,
    "proxy": {
        "timestamp": 1702129361444,
        "region": "cdg1",
        "method": "GET",
        "vercelCache": "MISS",
        "statusCode": 200,
        "referer": "https://my-app.vercel.app",
        "path": "/api/hello",
        "host": "my-app.vercel.app",
        "scheme": "https",
        "clientIp": "xx.xx.xx.xx",
        "userAgent": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        ],
    },
    "projectId": "prj_xxxxxxxxxxxxxxxxxxxxxx",
    "deploymentId": "dpl_xxxxxxxxxxxxxxxxxxxxxx",
    "source": "lambda",
    "host": "my-app.vercel.app",
    "path": "api/hello",
}

expected_log_entry = {
    "id": "1669118385998052846361484418",
    "message": "SAMPLE MESSAGE: START RequestId: xxxxxxxxxxxxxxxxx Version: $LATEST\nEND RequestId: xxxxxxxxxxxxxxxxx\nREPORT RequestId: xxxxxxxxxxxxxxxxx\tDuration: 1472.20 ms\tBilled Duration: 1473 ms\tMemory Size: 1024 MB\tMax Memory Used: 147 MB\t\n",
    "timestamp": {"seconds": 1702129361, "nanos": 444000000},
    "requestId": "cdg1::iad1::xxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxx",
    "statusCode": 200,
    "proxy": {
        "timestamp": 1702129361444,
        "region": "cdg1",
        "method": "GET",
        "vercelCache": "MISS",
        "statusCode": 200,
        "referer": "https://my-app.vercel.app",
        "path": "/api/hello",
        "host": "my-app.vercel.app",
        "scheme": "https",
        "clientIp": "xx.xx.xx.xx",
        "userAgent": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
        ],
    },
    "projectId": "prj_xxxxxxxxxxxxxxxxxxxxxx",
    "deploymentId": "dpl_xxxxxxxxxxxxxxxxxxxxxx",
    "source": "lambda",
    "host": "my-app.vercel.app",
    "path": "api/hello",
    "severity": "INFO",
    "http_request": {
        "requestMethod": "GET",
        "requestUrl": "https://my-app.vercel.app//api/hello",
        "status": 200,
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "remoteIp": "xx.xx.xx.xx",
        "referer": "https://my-app.vercel.app",
        "cacheHit": False,
    },
    "logging.googleapis.com/trace": f"projects/{project}/traces/cdg1::iad1::xxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxx",
}

log_entry = transform(vercel_log, project=project)
assert log_entry == expected_log_entry
print("succeess")
