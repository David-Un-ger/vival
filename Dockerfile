FROM ghcr.io/astral-sh/uv:debian

WORKDIR /uv

RUN apt update && apt install -y python3.11-dev libpq-dev gcc  # for psycopg2

COPY pyproject.toml ./
RUN uv sync

WORKDIR /workspace
