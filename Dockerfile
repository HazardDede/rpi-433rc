# FROM arm32v7/python:3.5-slim-stretch
FROM python:3.5-slim-stretch

# Setup workdir
ENV WORKDIR /rpi-433rc
ENV PYTHONPATH=${WORKDIR}
ENV CONFIG_DIR=/conf

RUN apt-get update -yy && \
    apt-get install -yy libc6-dev gcc

RUN mkdir -p ${WORKDIR}
WORKDIR ${WORKDIR}

# Copy the requirements file over to be a single layer
# This prevents that the layer is rebuild when ANY file has changed
COPY requirements.txt .

RUN pip3 install \
    --extra-index-url https://www.piwheels.hostedpi.com/simple \
    -r requirements.txt


# Install the rest of the application
COPY . .

# Re-copy the entrypoint.sh to the root
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint defaults to bash
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

