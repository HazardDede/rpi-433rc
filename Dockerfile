FROM arm32v7/python:3.6-slim-stretch

# Setup workdir
ENV WORKDIR /rpi-433rc

# Setting correct entrypoint
# ENV FLASK_APP ${WORKDIR}/rpi433rc/app.py
ENV PYTHONPATH=${WORKDIR}
ENV FLASK_MODULE=rpi433rc.app:app

RUN mkdir -p ${WORKDIR} && \
    cd ${WORKDIR}

# Install rest-api wrapper for rpi-rf
COPY . ${WORKDIR}

RUN apt-get update -yy && \
    apt-get install -yy libc6-dev gcc

RUN pip3 install \
    --extra-index-url https://www.piwheels.hostedpi.com/simple \
    -r ${WORKDIR}/requirements.txt

# Re-copy the entrypoint.sh to the root
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint defaults to bash
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

