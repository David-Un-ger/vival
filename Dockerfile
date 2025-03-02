FROM ghcr.io/astral-sh/uv:debian

WORKDIR /workspace

RUN apt update && apt install -y python3.11-dev libpq-dev gcc  # for psycopg2
#COPY . .
#RUN uv sync

#CMD ["uv", "run", "src/app.py"]
#EXPOSE 8050
