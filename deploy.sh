#!/bin/bash

function prompt() {
  echo "Deploying prompt"
  gcloud functions deploy prompt \
    --gen2 --runtime=python310 --trigger-http \
    --source=./functions/prompt --entry-point=prompt \
    "--service-account=$SERVICE_ACCOUNT" \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest 
}

function frames() {
  echo "Deploying frames"
  gcloud functions deploy frames \
    --gen2 --runtime=python310 --trigger-http \
    --source=./functions/frames --entry-point=frames \
    "--service-account=$SERVICE_ACCOUNT" \
    --update-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest --set-env-vars "GCP_BUCKET_NAME=$GCP_BUCKET_NAME"
}

function gateway() {
  echo "Deploying gateway"
  gcloud api-gateway api-configs create memegen --api=memegen \
    --openapi-spec=./openapi2-functions.yaml \
    "--backend-auth-service-account=$SERVICE_ACCOUNT"

  gcloud api-gateway gateways create memegen --api=memegen --api-config=memegen --location=us-central1
}

set -o allexport && source ./.env && set +o allexport

prompt
frames
gateway