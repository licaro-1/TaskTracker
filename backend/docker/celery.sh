#!/bin/bash

if [[ "${1}" == "celery" ]]; then
  celery --app=notifications.notification:celery_app worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  until timeout 10s celery --app=notifications.notification:celery_app inspect ping; do
    >&2 echo "Celery worker not available"
  done
  celery --app=notifications.notification:celery_app flower
fi