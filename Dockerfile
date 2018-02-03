FROM arm32v7/python:3.6-jessie

ENV RPIRF_VERSION 0.9.6

# Setup workdir
ENV WORKDIR /rpi-433rc
RUN mkdir -p ${WORKDIR} && \
    cd ${WORKDIR}

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install necessary dependencies
RUN pip3 install rpi-rf==${RPIRF_VERSION}

# Install rest-api wrapper for rpi-rf
# Not yet implemented

# Entrypoint defaults to bash
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

