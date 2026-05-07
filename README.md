![CI Pipeline](https://github.com/cs-uh-2012-spring26/cs-uh-2012-software-engineering-group_b/actions/workflows/ci.yml/badge.svg)

# Fitness Class Management System

A full-stack fitness class booking platform built with **Flask-RESTX** (backend API) and **React** (frontend). Users can register, browse fitness classes, book sessions, and receive reminders via email or Telegram. Trainers and admins can create classes (including recurring ones) and send notifications to attendees.

> **Bonus Frontend deployed at:** `http://<VM_IP>:3000` *(update this URL once your VM is provisioned)*

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Tech Stack](#tech-stack)
4. [Running with Docker (Recommended)](#running-with-docker-recommended)
5. [Running Locally (Without Docker)](#running-locally-without-docker)
6. [Frontend Development](#frontend-development)
7. [Environment Variables](#environment-variables)
8. [API Endpoints](#api-endpoints)
9. [Authentication & Authorization](#authentication--authorization)
10. [Recurring Classes (Feature 6)](#recurring-classes-feature-6)
11. [Telegram Notifications (Feature 7)](#telegram-notifications-feature-7)
12. [CI/CD Pipeline](#cicd-pipeline)
13. [Running Tests](#running-tests)

---

## Features

1. **User Registration & Login** — JWT-based auth with role assignment (member, trainer, admin)
2. **View Fitness Classes** — Public class listing with availability info
3. **Book a Class** — Members can RSVP to any class with available spots
4. **Create a Class** — Trainers and admins can create one-time or recurring classes
5. **View Class Bookings** — Trainers and admins can see who has booked a class
6. **Recurring Classes** — Create daily or weekly repeating classes with an end date
7. **Configurable Notifications** — Per-user opt-in for Email and/or Telegram reminders
8. **React Frontend** — GUI for login/logout, browsing classes, booking, and creating classes

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml                     # CI pipeline (runs tests on every push/PR to main)
├── app/
│   ├── __init__.py                    # Flask app factory, JWT + CORS setup
│   ├── config.py                      # Environment-driven configuration
│   ├── exceptions.py                  # Custom exception hierarchy
│   ├── apis/
│   │   ├── __init__.py                # Shared API constants
│   │   ├── auth.py                    # Auth endpoints (register, login, telegram link)
│   │   ├── booking.py                 # Booking endpoints
│   │   ├── decorators.py              # Role-based JWT access control
│   │   └── fitness_class.py           # Class endpoints (list, create, reminders)
│   ├── db/
│   │   ├── __init__.py                # DB client (mongomock or pymongo)
│   │   ├── bookings.py                # Booking collection queries
│   │   ├── constants.py               # Shared DB constants
│   │   ├── fitness_classes.py         # Fitness class collection queries
│   │   ├── telegram_links.py          # One-time Telegram link tokens
│   │   ├── users.py                   # User collection queries
│   │   └── utils.py                   # Serialization helpers
│   └── services/
│       ├── auth_service.py            # Registration and login logic
│       ├── booking_service.py         # Class booking logic
│       ├── email_reminders.py         # SendGrid email delivery
│       ├── fitness_class_service.py   # Class creation and reminder dispatch
│       ├── notification_service.py    # Multi-channel notification strategy
│       ├── telegram_link_service.py   # Telegram deep-link generation
│       └── token_service.py           # Invite token validation
├── frontend/
│   ├── src/
│   │   ├── api/client.js              # Axios instance (proxy-aware, auto-injects JWT)
│   │   ├── context/AuthContext.jsx    # JWT auth state (login, logout, role)
│   │   ├── components/
│   │   │   ├── Navbar.jsx             # Top navigation bar
│   │   │   └── ProtectedRoute.jsx     # Route guard for authenticated pages
│   │   └── pages/
│   │       ├── LoginPage.jsx          # Login form
│   │       ├── RegisterPage.jsx       # Registration form
│   │       ├── ClassesPage.jsx        # Class listing + booking
│   │       └── CreateClassPage.jsx    # Create class form (trainer/admin)
│   ├── Dockerfile                     # Multi-stage build: Node → nginx
│   ├── nginx.conf                     # nginx config with API proxy_pass to backend
│   ├── package.json
│   └── vite.config.js                 # Vite dev server with proxy to backend
├── tests/
│   ├── unit/
│   │   ├── conftest.py                # Pytest fixtures
│   │   ├── test_auth_api.py
│   │   ├── test_booking_api.py
│   │   ├── test_email_reminders_service.py
│   │   ├── test_fitness_api.py
│   │   └── test_general.py
│   └── utils.py
├── reports/
│   ├── final_reflection.md            # Sprint 4 team reflection
│   └── ...                            # Prior sprint reports
├── Dockerfile                         # Backend Docker image (Python 3.12 + Flask)
├── docker-compose.yml                 # Orchestrates mongo + api + frontend (+ telegram_bot)
├── telegram_bot.py                    # Telegram bot long-polling process
├── seed_db.py                         # Seed the database with sample data
├── makefile
├── requirements.txt
└── requirements-dev.txt
```

---

## Tech Stack

**Backend**
- [Flask-RESTX](https://flask-restx.readthedocs.io/) — REST API with auto-generated Swagger UI
- [PyMongo](https://pymongo.readthedocs.io/) — MongoDB driver
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) — JWT authentication
- [Flask-CORS](https://flask-cors.readthedocs.io/) — Cross-origin resource sharing
- [SendGrid Python SDK](https://github.com/sendgrid/sendgrid-python) — Email reminders
- [bcrypt](https://pypi.org/project/bcrypt/) — Password hashing

**Frontend**
- [React 18](https://react.dev/) — UI library
- [Vite](https://vitejs.dev/) — Build tool and dev server
- [React Router v6](https://reactrouter.com/) — Client-side routing
- [Axios](https://axios-http.com/) — HTTP client

**Infrastructure**
- [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) — Containerization
- [MongoDB 7](https://www.mongodb.com/) — Database (official Docker image)
- [nginx](https://nginx.org/) — Frontend static server + API reverse proxy
- [GitHub Actions](https://docs.github.com/actions) — CI/CD

**Testing**
- [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/) — Test runner and coverage
- [mongomock](https://github.com/mongomock/mongomock) — In-memory MongoDB for tests
- [pytest-mock](https://pytest-mock.readthedocs.io/) — Mocking utilities

---

## Running with Docker (Recommended)

Docker Compose starts everything — MongoDB, the Flask API, and the React frontend — with a single command. **No local Python or Node installation required.**

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the repository

```sh
git clone <repo-url>
cd cs-uh-2012-software-engineering-group_b
```

### 2. Set environment variables

Create a `.env` file in the project root (copy from `.envexample`):

```sh
cp .envexample .env
```

Edit `.env` and fill in your secrets:

```env
DB_NAME=eventsref_dev
DEBUG=true
JWT_SECRET_KEY=your-secret-key-here

# SendGrid (required for email reminders)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@coachly.dev
SENDGRID_ACCOUNT_EMAIL=your@email.com

# Telegram (optional — only needed for Telegram reminders)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

> `MONGO_URI` is not required in the `.env` — Docker Compose sets it automatically to connect the API to the MongoDB container.

### 3. Start all services

```sh
docker compose up --build
```

This starts:
| Service | URL |
|---------|-----|
| React Frontend | http://localhost:3000 |
| Flask API | http://localhost:8001 |
| Swagger UI | http://localhost:8001/swagger.json |
| MongoDB | localhost:27017 (internal) |

### 4. (Optional) Start the Telegram bot

The Telegram bot is a separate service that must be opted into explicitly:

```sh
docker compose --profile telegram up --build
```

### 5. Stop all services

```sh
docker compose down
```

To also delete the database volume:

```sh
docker compose down -v
```

---

## Running Locally (Without Docker)

### Prerequisites

- Python 3.10 or higher
- MongoDB running locally. Install from [mongodb.com/docs/manual/installation](https://www.mongodb.com/docs/manual/installation/) and start with:
  - **macOS:** `brew services restart mongodb-community`
  - **Linux:** `sudo systemctl restart mongod`
  - **Windows:** Start via Services or `mongod` in a terminal

### Setup

1. Copy the environment file and fill in your values:
   ```sh
   cp .envexample .env
   # Edit .env with your values
   ```

2. Create a virtual environment and install dependencies:
   ```sh
   make dev_env
   ```

### Run the backend

```sh
make run_local_server
```

This runs the test suite first, then starts Flask at [http://127.0.0.1:8000](http://127.0.0.1:8000).

To skip tests and run directly:

```sh
source .venv/bin/activate        # Mac/Linux
# or: . .venv/Scripts/activate   # Windows
FLASK_APP=app flask run --debug --host=0.0.0.0 --port 8000
```

### (Optional) Seed the database

```sh
python seed_db.py
```

---

## Frontend Development

The React frontend lives in the `frontend/` directory. It communicates with the Flask backend through a proxy — no CORS configuration needed.

### Prerequisites

- [Node.js 20+](https://nodejs.org/)
- The Flask backend running on port 8000

### Setup and run

```sh
cd frontend
npm install
npm run dev
```

The frontend is available at [http://localhost:5173](http://localhost:5173). The Vite dev server automatically proxies all `/auth/`, `/classes/`, and `/bookings/` requests to the Flask backend at `http://localhost:8000`.

### Frontend pages

| Route | Page | Access |
|-------|------|--------|
| `/` | Redirects to `/classes` | All |
| `/login` | Login form | Public |
| `/register` | Registration form | Public |
| `/classes` | Class listing + Book button | All (booking: members only) |
| `/classes/create` | Create class form | Trainer / Admin only |

### Build for production

```sh
cd frontend
npm run build
```

The built files go to `frontend/dist/`. In Docker, nginx serves these files and proxies API calls to the backend automatically.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | Yes (local) | MongoDB connection string. Set automatically in Docker. |
| `DB_NAME` | Yes | Database name (e.g., `eventsref_dev`) |
| `MOCK_DB` | Yes | `"true"` uses in-memory mock (for tests); `"false"` uses real MongoDB |
| `DEBUG` | Yes | Flask debug mode (`"true"` or `"false"`) |
| `JWT_SECRET_KEY` | Yes | Secret key for signing JWTs — keep this private |
| `SENDGRID_API_KEY` | Yes | SendGrid API key for sending email reminders |
| `SENDGRID_FROM_EMAIL` | Yes | Sender address for reminder emails |
| `SENDGRID_ACCOUNT_EMAIL` | Yes | Your SendGrid account email |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram Bot API token — required only for Telegram reminders |

---

## API Endpoints

The Swagger UI (interactive docs) is available at `http://localhost:8001` (Docker) or `http://localhost:8000` (local).

### Auth — `/auth`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/auth/register` | Register new user, returns JWT | Public |
| POST | `/auth/login` | Login, returns JWT | Public |
| POST | `/auth/validate-token` | Validate an invite token | Public |
| POST | `/auth/notification-preferences` | Update email/Telegram opt-ins | Authenticated |
| POST | `/auth/telegram-link/start` | Generate one-time Telegram deep-link | Authenticated |

### Classes — `/classes`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/classes/` | List all fitness classes | Public |
| POST | `/classes/` | Create a class (supports recurrence) | Trainer / Admin |
| POST | `/classes/<class_id>/reminders` | Send reminders to class attendees | Trainer |

### Bookings — `/bookings`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/bookings/` | Book a fitness class | Member |
| GET | `/bookings/class/<class_id>` | View all bookings for a class | Trainer / Admin |

---

## Authentication & Authorization

This API uses **JWT (JSON Web Tokens)** for stateless authentication and role-based access control.

### Roles

| Role | Can Do |
|------|--------|
| `member` | View classes, book classes, update notification preferences |
| `trainer` | All member actions + create classes, view bookings, send reminders |
| `admin` | All trainer actions |

### Registration & Role Assignment

Roles are assigned at registration using invite tokens:

| Token | Role Granted |
|-------|-------------|
| *(no token)* | `member` |
| `trainer-secret-123` | `trainer` |
| `admin-secret-456` | `admin` |

Example registration payload:
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword",
  "token": "trainer-secret-123"
}
```

### Using the JWT

After registering or logging in, include the returned `access_token` in all protected requests:

```
Authorization: Bearer <your_jwt_here>
```

**In Swagger UI:** Click **Authorize** (top right) and enter `Bearer <your_jwt_here>`.

---

## Recurring Classes (Feature 6)

Trainers can create classes that repeat daily or weekly by setting `recurrence_type` and `recurrence_end_date` in the create class request.

### Create class payload

```json
{
  "title": "Morning Yoga",
  "datetime": "2027-02-20T09:00:00Z",
  "capacity": 20,
  "trainer_name": "Alex Trainer",
  "recurrence_type": "weekly",
  "recurrence_end_date": "2027-06-20T09:00:00Z"
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `recurrence_type` | `one_time`, `daily`, `weekly` | How often the class repeats |
| `recurrence_end_date` | ISO 8601 date string | Last date for recurring instances (required if recurrence is not `one_time`) |

The system generates individual class records for each occurrence, each bookable independently. Each instance decrements its own `available_spots` when booked.

**In the frontend:** The Create Class form shows the recurrence end date field automatically when you select Daily or Weekly.

---

## Telegram Notifications (Feature 7)

Users can opt into Telegram reminders in addition to (or instead of) email. Each user controls their own notification channels.

### Setup

1. Set `TELEGRAM_BOT_TOKEN` in your `.env`.
2. Start the Telegram bot process:
   - **Docker:** `docker compose --profile telegram up`
   - **Local:** `python telegram_bot.py` (in a separate terminal)

### Linking a Telegram account

Complete these steps as the user who wants to receive Telegram reminders:

1. **Authenticate** and call `POST /auth/telegram-link/start` (requires JWT).
2. The response contains a `deep_link` URL (e.g., `https://t.me/CoachlyyBot?start=<token>`).
3. **Open the deep link** — this redirects you to the Telegram bot.
4. **Tap Start** in Telegram — this consumes the one-time token and links your chat ID.
5. **Enable Telegram** by calling `POST /auth/notification-preferences`:

```json
{
  "notification_preferences": {
    "email": false,
    "telegram": true
  }
}
```

### Triggering reminders

A trainer calls `POST /classes/<class_id>/reminders` with their JWT. The system checks each attendee's preferences and dispatches via the enabled channels (email and/or Telegram).

**Frontend integration example** (connect Telegram button):

```js
const res = await fetch('/auth/telegram-link/start', {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` },
})
const { deep_link } = await res.json()
window.location.href = deep_link
```

> **Notes:**
> - Telegram linking tokens are one-time use and expire quickly. Regenerate if expired.
> - If `TELEGRAM_BOT_TOKEN` is missing or invalid, Telegram reminder dispatch will fail at send time.
> - Email and Telegram can both be enabled simultaneously.

---

## CI/CD Pipeline

### Continuous Integration

The CI pipeline runs automatically on every push and pull request to `main`.

**Workflow file:** `.github/workflows/ci.yml`

**What it does:**
1. Checks out the repository
2. Sets up Python 3.10
3. Installs `requirements.txt` and `requirements-dev.txt`
4. Runs the full test suite with coverage: `pytest -vv --cov=app tests/`

**Environment for CI:** Uses `MOCK_DB=true` (mongomock, no real DB needed). The app accepts `DB_URI` (preferred) and `MONGO_URI` (backward-compatible), and CI injects secrets via GitHub Actions.

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Purpose |
|--------|---------|
| `MONGO_URI` | MongoDB URI secret used by CI (`DB_URI` is populated from this value) |
| `JWT_SECRET_KEY` | JWT signing secret |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | Sender email address |
| `SENDGRID_ACCOUNT_EMAIL` | SendGrid account email |

### Continuous Deployment (Production VM over SSH)

The CD workflow (`.github/workflows/cd.yml`) deploys only **after** the CI workflow succeeds on `main` (and can also be run manually from **Actions → CD Pipeline → Run workflow**).

Deployment steps:
1. Connect to the production VM via SSH (PEM private key from GitHub Secret)
2. Clone repo if missing, otherwise pull latest `main`
3. Run `sudo docker compose down`
4. Run `sudo docker compose up -d --build --remove-orphans`

Add these CD secrets in GitHub:

| Secret | Purpose |
|--------|---------|
| `PROD_HOST` | Production server public IP or DNS |
| `PROD_USER` | SSH username on the server (for example `ubuntu`) |
| `PROD_SSH_KEY` | Full PEM private key content used for SSH authentication |
| `PROD_APP_DIR` | Absolute path to the deployed repo on the server |
| `PROD_DB_URI` | Production DB URI (optional for this compose setup, kept for env parity) |
| `PROD_DB_NAME` | Production `DB_NAME` value |
| `PROD_DEBUG` | Production `DEBUG` value (usually `false`) |
| `PROD_JWT_SECRET_KEY` | Production JWT secret |
| `PROD_SENDGRID_API_KEY` | Production SendGrid API key |
| `PROD_SENDGRID_FROM_EMAIL` | Production sender email |
| `PROD_SENDGRID_ACCOUNT_EMAIL` | Production SendGrid account email |
| `PROD_TELEGRAM_BOT_TOKEN` | Production Telegram bot token |

---

## Running Tests

```sh
make tests
```

Or directly with pytest:

```sh
pytest -vv --cov=app tests/
```

View the HTML coverage report:

```sh
open htmlcov/index.html     # Mac
start htmlcov/index.html    # Windows
```

Run a specific test file:

```sh
pytest tests/unit/test_fitness_api.py -q
pytest tests/unit/test_booking_api.py -q
pytest tests/unit/test_email_reminders_service.py -q
```

Tests use `MOCK_DB=true` via environment configuration, so no MongoDB installation is needed to run tests.
