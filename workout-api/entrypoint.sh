#!/bin/bash


# Populate Database
python seed.py


# Run FastAPI 
exec uvicorn main:app --host 0.0.0.0 --port 8000
