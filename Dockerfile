FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS prod
COPY . .
CMD ["gunicorn","eventify.wsgi:application","--bind","0.0.0.0:8000"]
