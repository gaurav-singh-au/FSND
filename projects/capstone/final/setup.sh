#!/bin/sh
export FLASK_APP=./src/api.py
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0

