FROM python:3.11-slim

ENV POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --without dev --no-root

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
