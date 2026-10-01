FROM buildkite/agent:3.138.0-ubuntu
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/otel-requirements.txt
RUN python3 -m venv /opt/otel-venv \
    && /opt/otel-venv/bin/pip install --no-cache-dir -r /tmp/otel-requirements.txt
