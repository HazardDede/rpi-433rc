#!/usr/bin/env bash

export FLASK_APP=`pwd`/rpi433rc/app.py

flask run --host=0.0.0.0