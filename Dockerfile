FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

# Add mount point for data volume
VOLUME /data

CMD [ "python3", "server.py" ] & [ "python3", "sldserver.py" ]

FROM builder as dev-envs