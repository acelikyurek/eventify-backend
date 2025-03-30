# Eventify Backend

A backend management API built with Python Django framework. Key technologies used in this project include:

- REST endpoints for CRUD on events & registrations

- GraphQL read‑only queries for flexible data fetching

- JWT authentication

- Asynchronous email notifications (Celery + Redis)

- Caching (Redis) for high‑performance listing

- Metrics (Prometheus) & structured logging

- Containerized via Docker & Docker Compose

- Test suite (`pytest`) with coverage reporting

## Prerequisites

- Install Docker Desktop or Docker Engine with Compose support.

- Create a file for environment variables (`.env`) in project root.

    ```bash
    DJANGO_SECRET_KEY=<...>
    DJANGO_DEBUG=True
    DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

    POSTGRES_DB=eventify
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=password
    POSTGRES_HOST=db
    POSTGRES_PORT=5432

    REDIS_HOST=redis
    REDIS_PORT=6379

    CELERY_BROKER_URL=redis://redis:6379/0

    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USER=<...>
    EMAIL_PASSWORD=<...>
    ```

## Setup

1. Build and start all services:

    ```bash
    docker compose up --build -d
    ```

2. Apply `makemigrations` & `migrate`

    ```bash
    docker compose exec web python manage.py makemigrations
    docker compose exec web python manage.py migrate
    ```

3. Run the full test suite (with coverage):

    ```bash
    docker compose exec web pytest
    ```

## API Endpoints

| Method | Endpoint                               | Description                   |
| ------ | -------------------------------------- | ----------------------------- |
| POST   | `/api/auth/login`                      | Login an existing user        |
| POST   | `/api/auth/register`                   | Register a new user           |
| GET    | `/api/events`                          | List events (cached)          |
| POST   | `/api/events`                          | Create event (organizer only) |
| GET    | `/api/events/{id}`                     | Retrieve event details        |
| PUT    | `/api/events/{id}`                     | Update event (organizer only) |
| DELETE | `/api/events/{id}`                     | Delete event (organizer only) |
| POST   | `/api/events/{event_id}/registrations` | Register for an event         |
| DELETE | `/api/events/{event_id}/registrations` | Cancel registration           |
| GET    | `/api/registrations`                   | List user's registrations     |
