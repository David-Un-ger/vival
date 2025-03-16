FROM ghcr.io/astral-sh/uv:debian


# build the venv in /uv/.venv
WORKDIR /uv
RUN apt update && apt install -y python3.11-dev libpq-dev gcc  # for psycopg2
COPY pyproject.toml ./
RUN uv sync

# later mount the workspace to /workspace
WORKDIR /workspace
