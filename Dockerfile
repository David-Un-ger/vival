FROM ghcr.io/astral-sh/uv:debian

WORKDIR /workspace

COPY . .
RUN uv sync

CMD ["uv", "run", "src/app.py"]
EXPOSE 8050
