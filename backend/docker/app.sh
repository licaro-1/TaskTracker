#!/bin/bash

alembic upgrade head

#python cli.py load_statuses


gunicorn main:main_app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000