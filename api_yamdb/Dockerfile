FROM python:3.7-slim


WORKDIR /app

COPY requirements.txt /app

# Выполнить установку зависимостей внутри контейнера.
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
RUN pip3 install -r /app/requirements.txt --no-cache-dir


COPY ./ ./


CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]