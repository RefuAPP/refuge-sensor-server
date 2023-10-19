#!/bin/bash
sleep 10
python setup_database.py
uvicorn api:app --host 0.0.0.0 --port 8000
