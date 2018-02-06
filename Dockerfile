FROM arm32v7/python:3.6-jessie

ENV RPIRF_VERSION 0.9.6

# Setup workdir
ENV WORKDIR /rpi-433rc
RUN mkdir -p ${WORKDIR} && \
    cd ${WORKDIR}


# Install rest-api wrapper for rpi-rf
COPY . ${WORKDIR}
RUN pip3 install -r ${WORKDIR}/requirements.txt
# Setting correct entrypoint
ENV FLASK_APP ${WORKDIR}/rpi433rc/app.py

# Re-copy the entrypoint.sh to the root
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint defaults to bash
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

