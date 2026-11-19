#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
umask 077

if [ -e .env ]; then
    printf '%s\n' '.env already exists; keeping its settings and secret key.'
    exit 0
fi

# Docker is the only prerequisite; no host Python installation is needed.
blog_secret_key=$(docker run --rm python:3.12-slim python -c 'import secrets; print(secrets.token_urlsafe(64))')
sed "s/^SECRET_KEY=$/SECRET_KEY=$blog_secret_key/" .env.example > .env
printf '%s\n' 'Created private .env. Start the app with: docker compose up --build -d --wait'
