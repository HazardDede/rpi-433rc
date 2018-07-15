#!/bin/bash

case ${1} in
    sniff)
      shift
      exec rpi-rf_receive "$@"
      ;;
    serve)
      exec gunicorn --workers 4 --bind 0.0.0.0:5000 ${FLASK_MODULE}
      ;;
    *)
      exec "$@"
      ;;
esac
