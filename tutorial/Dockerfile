FROM buildkite/agent:3-ubuntu@sha256:2d9264bdfddd9135f785f09281a0e891fcb620104c01fccc64d491da47c0d7f7
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/otel-requirements.txt
RUN python3 -m venv /opt/otel-venv \
    && /opt/otel-venv/bin/pip install --no-cache-dir -r /tmp/otel-requirements.txt
