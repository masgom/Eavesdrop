FROM python:3.14-slim-trixie

WORKDIR /eavesdrop
COPY . .

RUN apt-get update && apt-get install -y ffmpeg

# Remove apt cache to maintain a small image
RUN rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv sync --frozen --no-dev

CMD [ "uv", "run", "eavesdrop.py", "-OO" ]
