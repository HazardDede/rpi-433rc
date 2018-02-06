#!/bin/bash

case ${1} in
    sniff)
      shift
      exec rpi-rf_receive "$@"
      ;;
    serve)
      exec flask run --host=0.0.0.0
      ;;
    *)
      exec "$@"
      ;;
esac
