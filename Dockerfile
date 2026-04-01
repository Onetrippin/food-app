FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VERSION=1.8.4 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app/src \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl build-essential libpq-dev postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python -

COPY pyproject.toml README.md /app/

RUN poetry install --only main --no-root --no-interaction --no-ansi

COPY . /app

ENTRYPOINT ["sh", "/app/scripts/entrypoint.sh"]
