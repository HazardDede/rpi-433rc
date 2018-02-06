#!/bin/bash

case ${1} in
    sniff)
      shift
      exec rpi-rf_receive "$@"
      ;;
    serve)
      echo "Serving via rest-api is not implemented"
      exec ${WORKDIR}/run.sh
      ;;
    *)
      exec "$@"
      ;;
esac
