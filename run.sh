#!/usr/bin/env bash

gunicorn --workers 4 --bind 0.0.0.0:5000 rpi433rc.app:app