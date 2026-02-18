FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY demo /app/demo
COPY tests /app/tests

RUN pip install --upgrade pip && pip install -e '.[dev]'

EXPOSE 8000

CMD ["python", "demo/manage.py", "runserver", "0.0.0.0:8000"]
