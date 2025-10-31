FROM python:alpine

WORKDIR /app

RUN pip install poetry && addgroup app && adduser -S -G app app

COPY . .

RUN chown -R app:app .

USER app

RUN poetry install --no-root

ENV PORT=5000

ENTRYPOINT [ "poetry", "run", "gunicorn", "app:app" ]