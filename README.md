# Content Moderation API

A REST API that analyzes user-generated text and flags inappropriate content using a rule-based keyword detection system. Built as a backend engineering portfolio project demonstrating clean API design, database persistence, automated testing, schema migrations, and containerization with FastAPI, PostgreSQL, and Docker.

---

## Overview

Platforms that accept user-generated content (comments, reviews, chat messages, forum posts) need a way to screen that content before it's published. This project implements a simplified version of that moderation pipeline: it accepts a piece of text, checks it against a set of predefined keyword categories, stores the result in a database, and returns a structured verdict — whether the content was flagged, which category it falls into, and a confidence score.

This is a v1 implementation using rule-based keyword matching, not machine learning. The architecture is intentionally structured so the detection logic is isolated from the API and database layers, making it straightforward to swap in a more sophisticated detection method (e.g. an ML classifier) later without touching the rest of the system.

---

## Architecture

```
Client
  │
  ▼
FastAPI (routing, request/response validation)
  │
  ▼
Moderation Service (rule-based keyword detection)
  │
  ▼
SQLAlchemy ORM
  │
  ▼
PostgreSQL (persisted moderation results)
```

The project follows a layered structure with clear separation of concerns:

| Layer | File | Responsibility |
|---|---|---|
| API | `app/main.py` | Route definitions, request handling, HTTP status codes |
| Validation | `app/schemas.py` | Pydantic models defining the API's request/response contract |
| Business logic | `app/moderation.py` | Rule-based text analysis, framework-agnostic |
| Data access | `app/models.py` | SQLAlchemy ORM model mapping to the database table |
| Persistence | `app/database.py` | Database engine, session management |

This separation means the SQLAlchemy model (what's stored) and the Pydantic schema (what's exposed over the API) are defined independently, rather than being the same object reused everywhere — a deliberate design choice that keeps the public API contract decoupled from the internal database structure.

---

## Tech Stack

- **Python 3.12**
- **FastAPI** — web framework, request/response validation, auto-generated OpenAPI docs
- **PostgreSQL** — relational database for persisting moderation results
- **SQLAlchemy** — ORM for database models and queries
- **Alembic** — database schema migrations
- **Pydantic** — data validation and schema definitions
- **Uvicorn** — ASGI server
- **pytest** — automated testing framework
- **httpx** — HTTP client used by FastAPI's test client
- **Docker / Docker Compose** — containerization

---

## Features

- **`POST /moderate`** — accepts text, runs it through the rule-based moderation engine, persists the result, and returns it
- **`GET /moderation/{id}`** — retrieves a previously stored moderation result by ID
- **`GET /health`** — service health check endpoint
- Input validation: rejects missing, empty, or whitespace-only text with a `422` response
- Proper REST semantics: `404` for missing resources, `422` for invalid input
- Auto-generated interactive API documentation via Swagger UI (`/docs`)
- Automated test suite (pytest) covering happy paths, validation rules, and error handling, run against an isolated in-memory database
- Schema migrations managed with Alembic instead of ad-hoc table creation
- Fully containerized with Docker Compose; a pre-built image is also published to Docker Hub

---

## How the Moderation Logic Works

Incoming text is lowercased and checked against four predefined keyword categories:

| Category | Example triggers |
|---|---|
| `abusive` | insults and put-downs directed at a person |
| `hate_speech` | phrases associated with discriminatory language |
| `violence` | threats or violent language |
| `spam` | promotional, phishing, or scam-style phrasing |

For each category, the engine counts how many of its keywords appear in the text. The category with the most matches is returned. If no keywords match in any category, the text is marked `clean`. A simple confidence score is derived from the number of matched keywords (capped below 1.0, since keyword matching alone should never claim full certainty).

**Known limitation:** this approach only catches content containing its exact predefined keywords. It cannot detect synonyms, misspellings, sarcasm, or context — for example, "you are terrible at this" would not be flagged unless "terrible" is explicitly in the keyword list. It's also prone to false positives on words that are contextually broad (e.g. "kill" appearing in "this song kills it"). This is a deliberate, acknowledged tradeoff of rule-based systems, and the exact reason production moderation systems typically move toward ML-based classifiers — which this architecture is structured to accommodate later without redesigning the API or database layers.

**On authentication:** `GET /moderation/{id}` uses sequential integer IDs, which means an unauthenticated retrieval endpoint would allow enumeration of every stored result (requesting `/moderation/1`, `/moderation/2`, etc.). This was identified during development as a real access-control gap; API key authentication on this endpoint specifically is documented as a near-term improvement below. `POST /moderate` is left open since it only ever returns the caller's own submission.

---

## Database Schema

**Table: `moderation_results`**

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing identifier |
| `text` | String | The original submitted text |
| `is_flagged` | Boolean | Whether the text was flagged |
| `category` | String | Detected category (`abusive`, `hate_speech`, `violence`, `spam`, or `clean`) |
| `confidence` | Float | Heuristic confidence score (0.0–0.95) |
| `created_at` | DateTime | Server-generated timestamp of when the record was created |

Schema changes are managed with **Alembic** migrations rather than relying on `Base.metadata.create_all()`, so future changes to this table (new columns, index changes, etc.) can be applied incrementally and are version-controlled.

---

## API Reference

### `POST /moderate`

**Request:**
```json
{
  "text": "You are such an idiot"
}
```

**Response — `200 OK`:**
```json
{
  "id": 1,
  "text": "You are such an idiot",
  "is_flagged": true,
  "category": "abusive",
  "confidence": 0.65,
  "created_at": "2026-09-01T13:03:42.372176+05:30"
}
```

**Validation errors — `422 Unprocessable Entity`:** returned when `text` is missing, empty, or whitespace-only.

---

### `GET /moderation/{id}`

Retrieves a previously stored moderation result.

**Response — `200 OK`:** same shape as the `POST /moderate` response.

**Response — `404 Not Found`:**
```json
{
  "detail": "Moderation result not found"
}
```

---

### `GET /health`

**Response — `200 OK`:**
```json
{
  "status": "ok"
}
```

---

## Project Structure

```
content-moderation-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app and route definitions
│   ├── database.py       # DB engine, session, and connection setup
│   ├── models.py         # SQLAlchemy ORM model
│   ├── schemas.py        # Pydantic request/response schemas
│   └── moderation.py     # Rule-based moderation logic
│
├── alembic/
│   ├── versions/          # Migration scripts
│   └── env.py             # Alembic environment configuration
├── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures and in-memory test database setup
│   └── test_main.py      # Endpoint tests (happy paths, validation, error handling)
│
├── requirements.txt
├── .env                   # Environment variables (not committed)
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (a local install, or run it via Docker as shown below)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Chhamatomar/content_moderation_api.git
   cd content_moderation_api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1      # Windows PowerShell
   # source venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://postgres:<password>@localhost:5432/<database_name>
   ```

5. **Start PostgreSQL** (skip if already running locally)
   ```bash
   docker run --name moderation-postgres -e POSTGRES_PASSWORD=<password> -e POSTGRES_DB=<database_name> -p 5432:5432 -d postgres:16
   ```

6. **Apply database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Open the interactive API docs**

   Visit `http://127.0.0.1:8000/docs`

### Running Tests

The test suite runs against an isolated in-memory SQLite database, so it does not require PostgreSQL to be running and will never affect real data.

```bash
pytest -v
```

---

## Dockerization

The project runs as two orchestrated services via Docker Compose:

* **`api`** — built from the included `Dockerfile` (Python 3.12-slim base), runs the FastAPI app via Uvicorn
* **`db`** — official `postgres:16` image, with a named volume (`moderation_pgdata`) for data persistence across restarts

The `api` service declares `depends_on: db`, so the database container starts before the API container. The two services communicate over Docker Compose's internal network using the service name `db` as the hostname, rather than `localhost`.

### Run the Full Stack with Docker Compose

```bash
docker-compose up --build
```

Once running, visit:
```
http://127.0.0.1:8080/docs
```

### Pull the Pre-Built Image from Docker Hub

A pre-built image is also published on Docker Hub, so the API can be pulled and run directly without building from source:

```bash
docker pull chhamatomar639/content-moderation-api:latest
docker run -p 8080:8000 --env-file .env chhamatomar639/content-moderation-api:latest
```

*(Requires a reachable `DATABASE_URL` in your `.env` — this runs the API container alone, without the bundled Postgres container that Docker Compose provides.)*

Docker Hub image: [chhamatomar639/content-moderation-api](https://hub.docker.com/r/chhamatomar639/content-moderation-api)

---

## What This Project Demonstrates

- Designing a layered backend architecture with clear separation between API, business logic, and data access
- Building a REST API with FastAPI, including request/response validation via Pydantic
- Modeling and persisting data with SQLAlchemy and PostgreSQL
- Handling REST error semantics correctly (`404`, `422`)
- Identifying and documenting the limitations of a rule-based system, and structuring the codebase so a more advanced detection method could be substituted later without a redesign
- Writing automated tests with pytest, using dependency overrides to isolate tests from the production database
- Managing schema changes with Alembic migrations instead of ad-hoc table creation
- Containerizing a Python web service with Docker Compose and publishing a usable image to Docker Hub
- Debugging real infrastructure issues (container port conflicts, database connectivity) encountered while building and running the project locally

---


## License

This project is available for portfolio and educational reference.
