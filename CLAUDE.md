# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Two-service Django application orchestrated by Docker Compose, fronted by an nginx reverse proxy.

```
[browser] → nginx (80/443) → / → frontend (Django, gunicorn :8000)
                            → /api/ → backend  (Django + DRF, gunicorn :8001)
                                          ↓
                                    Hugging Face Inference API
                                    (provider = Cerebras)
```

**Two separate Django projects, not one.** `backend/` and `frontend/` each have their own `core/` (settings, urls, wsgi), their own `requirements.txt`, and their own `manage.py`. They are deployed as independent containers and only communicate over HTTP through `BACKEND_API_URL` (defaults to `http://backend:8001/api` on the docker network). Do not import from one project into the other.

### Backend (`backend/`, Django REST Framework)
- App: `api/`. Owns the database (SQLite by default at `/app/data/db.sqlite3`, optional Postgres via `DATABASE_URL`).
- `api/services.py` — `HuggingFaceAPIService` is the integration boundary. If `HUGGING_FACE_API_TOKEN` is missing it auto-enters **demo mode** and returns prompt-keyword-routed canned strings instead of calling Cerebras. New models must be added to `AVAILABLE_MODELS` in `backend/core/settings.py` *and* (for demo mode to work) to the `mock_responses` dict in `services.py`.
- `api/views.py` exposes: `POST /api/prompt/`, `GET /api/models/`, `GET /api/responses/`, `GET /api/sessions/`, `GET /api/sessions/<id>/`, `GET /api/health/`. The prompt flow writes a `ModelResponse` per model and groups them under a `PromptSession` (M2M).
- DRF is wide open (`AllowAny`); the access control story lives entirely on the frontend.

### Frontend (`frontend/`, plain Django + templates)
- App: `chat/`. `chat/views.py:index` server-side fetches `/api/models/` from the backend and renders `templates/chat/index.html`. `chat/views.py:chat` is a thin POST proxy that forwards `{prompt, model_ids}` to `POST /api/prompt/`.
- Auth gate: `core/middleware.py:LoginRequiredMiddleware` is appended to `MIDDLEWARE` and **forces login for every path** except `/accounts/login/`, `/static/`, `/admin/`, `/favicon.ico`. New public routes must be added to its allowlist.
- Has its own SQLite DB at `/app/data/db.sqlite3` solely for Django's `auth_user`/sessions tables — do **not** put app data here, that belongs in the backend.

### nginx (`nginx/nginx.conf`)
- Hardcoded for `3chatbots.com`: 80→301→443, TLS via Let's Encrypt mounted from the host (`/etc/letsencrypt`). Routes `/api/` to backend, everything else to frontend. Changing the domain requires editing `server_name` and the cert paths together.

## Common commands

### Local dev (no Docker, two terminals)
```bash
# Backend (port 8000 by default)
cd backend && python manage.py migrate && python manage.py runserver

# Frontend (run on 3000 to match tests.py)
cd frontend && python manage.py runserver 3000
```
Both projects read `../.env` via `python-dotenv`; `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` are required or Django will raise `KeyError` at import.

### Docker (production-shaped)
```bash
docker compose up -d --build
docker compose exec frontend python manage.py migrate
docker compose exec frontend python manage.py createsuperuser   # for the login gate
docker compose ps
docker compose logs -f backend
```

### Tests
The `tests.py` files in `backend/` and `frontend/` are **not** Django `TestCase`s — they are interactive smoke scripts that hit live HTTP endpoints and prompt for input. Run with `python backend/tests.py` (expects backend on `:8000`) or `python frontend/tests.py` (expects backend on `:8000` and frontend on `:3000`). There is no automated test suite.

### Migrations
After model changes in `backend/api/models.py`:
```bash
cd backend && python manage.py makemigrations api && python manage.py migrate
```

## Working in this repo

- **Commit messages must not mention Claude** in any form: no `Co-Authored-By: Claude` trailer, no "Generated with Claude Code" line, no emoji bot signature. Commits should read as plain authored work.

## Things to know

- **Demo mode is silent.** Missing `HUGGING_FACE_API_TOKEN` doesn't error — it just returns mock strings prefixed with `"DEMO MODE"`. If responses look canned, check the token before debugging the API call.
- **Demo mode `mock_responses` dict only has entries for three of the four `AVAILABLE_MODELS`.** Selecting `openai/gpt-oss-120b` in demo mode will `AttributeError` because `model_responses.get(...)` returns `None`. Fix by adding an entry or guarding the lookup if you touch that path.
- **Two databases exist by design** (frontend = auth, backend = prompts/sessions). When `createsuperuser` is run on the *backend*, those credentials cannot log into the frontend UI — superusers must be created in the frontend container.
- **The deployment guide in `README.md` is authoritative for AWS/EC2 setup.** It includes a tear-down section with hardcoded ARNs/IDs from a prior deploy — generalize before reusing.
