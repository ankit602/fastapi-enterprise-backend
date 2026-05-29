#!/bin/sh
set -e

python -m app.init_db

exec celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
