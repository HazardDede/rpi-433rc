#!/bin/bash

case ${1} in
    sniff)
      shift
      exec rpi-rf_receive "$@"
      ;;
    serve)
      exec ./run.sh
      ;;
    *)
      exec "$@"
      ;;
esac
