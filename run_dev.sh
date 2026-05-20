#!/usr/bin/env bash
# POSIX shell helper to run Flask with debug + reload
export FLASK_APP=application
export FLASK_DEBUG=1
python -m flask --app application --debug run --reload --host=0.0.0.0
