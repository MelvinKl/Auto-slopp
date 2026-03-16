FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git gh openssh-client && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY src/ ./src/

RUN uv sync --no-dev

ENV AUTO_SLOPP_BASE_REPO_PATH=/repos

VOLUME ["/repos"]

ENTRYPOINT ["uv", "run", "auto-slopp"]
CMD []
