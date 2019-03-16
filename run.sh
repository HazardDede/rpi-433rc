#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
export PYTHONPATH=${BASEDIR}
python ${BASEDIR}/rpi433rc/runner.py --workers 1 --bind 0.0.0.0:5000