# vercel-google-cloud-logging

A publicly accessible HTTP endpoint, deployed to Google Cloud Functions, to serve as a Vercel [log drain](https://vercel.com/docs/observability/log-drains-overview) to ingest logs into Google Cloud Logging. This only converts some fields from the Vercel log to their Cloud Logging counterparts.

## Setup

(1) Generate a secret key of length 32 (minimum length allowed by Vercel):

```
python -c 'import secrets; print(secrets.token_hex(16))'
```

(2) Create file `env-vars.yaml` based on [env-vars.yaml.example](./env-vars.yaml.example) and set SECRET_KEY. You don't need to set VERCEL_VERIFICATION_KEY yet.

(3) Deploy url verifier to google cloud:

```
gcloud functions deploy vercel-log-drain \
  --gen2 \
  --runtime=python312 \
  --region=us-east4 \
  --trigger-http \
  --concurrency=10 \
  --cpu=1 \
  --memory="256MB" \
  --allow-unauthenticated \
  --env-vars-file=env-vars.yaml \
  --source=. \
  --entry-point=on_log
```

Wait for command to complete and copy the Cloud Function URL.

(4) Create a log drain in Vercel with the following options:

- Delivery Format: JSON
- Custom Secret: secret generated in step 1
- Endpoint: The URL of the Cloud Function deployed in step 3

When you enter the Endpoint URL, Vercel will ask you to verify that you own the URL. Set VERCEL_VERIFICATION_KEY in `env-vars.yaml` and redeploy (step 3). Wait for the deployment to finish then click Verify in Vercel.

(5) Redeploy (step 3)

## Development

Local testing:

1. Start the server `SECRET_KEY="TODO" functions-framework-python --target=on_log`
2. Make a request `curl localhost:8080`

Run tests:

```
python -m tests.test_transform
```

Useful documentation:

- Local testing https://cloud.google.com/functions/docs/create-deploy-http-python#build_and_test_your_function_locally
- Cloud Functions Python runtime https://cloud.google.com/functions/docs/concepts/python-runtime
- Vercel log drain auth https://vercel.com/docs/rest-api#securing-your-log-drains
