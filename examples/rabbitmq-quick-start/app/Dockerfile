FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "rabbitmq_quick_start.run"]
