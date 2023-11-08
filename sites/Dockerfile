FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app
COPY ../templates /app/templates
COPY ../.env /app/.env

# Add mount point for data volume
VOLUME /data

ENTRYPOINT ["python3"]
CMD ["sldserver.py"]

FROM builder as dev-envs