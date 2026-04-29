# 3Chatbots — interface to test multiple LLMs

Submit one prompt, compare responses from up to three Hugging Face / Cerebras language models side by side.

- **Local**: a single Django project under `app/`. `pip install`, `runserver`, done.
- **Live**: deployed on **Fly.io** (free tier) at `www.3chatbots.com`, with DNS hosted on **Netbeat**.
- **Demo mode**: if no `HUGGING_FACE_API_TOKEN` is set, the API service auto-falls-back to canned per-model responses so the UI is fully usable offline.

---

## Run locally

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
cp .env.example .env                  # then edit SECRET_KEY at minimum
cd app
python manage.py migrate
python manage.py createsuperuser      # the site requires login
python manage.py runserver
```

Open <http://127.0.0.1:8000>, log in, and submit a prompt.

### Live mode vs. demo mode

The app checks `HUGGING_FACE_API_TOKEN` on each request:

- **Token set** → calls Hugging Face Inference (Cerebras provider) for real responses.
- **Token unset / blank** → returns canned `"DEMO MODE …"` strings keyed by prompt content. No network call.

To switch, edit `.env` and restart `runserver`. No code change needed.

---

## Deploy live (Fly.io + Netbeat DNS)

One-time setup. Estimated cost on free tier: **$0/mo** at this traffic level.

### 1. Install flyctl and sign in

```bash
brew install flyctl       # or curl -L https://fly.io/install.sh | sh
fly auth signup           # or `fly auth login`
```

### 2. Launch the app

From the repo root:

```bash
fly launch --no-deploy --copy-config --name 3chatbots
fly volumes create data --size 1 --region fra
```

`--no-deploy` so we can set secrets first. `--copy-config` keeps the committed `fly.toml`. Pick the region nearest you (`fra` = Frankfurt — change in `fly.toml` if you prefer).

### 3. Set secrets

```bash
fly secrets set \
  SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
  ALLOWED_HOSTS="3chatbots.com,www.3chatbots.com,3chatbots.fly.dev" \
  CSRF_TRUSTED_ORIGINS="https://3chatbots.com,https://www.3chatbots.com,https://3chatbots.fly.dev" \
  HUGGING_FACE_API_TOKEN="hf_xxx"   # omit for demo mode
```

### 4. Deploy

```bash
fly deploy
fly ssh console -C "python manage.py createsuperuser"
fly status
```

### 5. Point Netbeat DNS at Fly

Get the Fly IPs:

```bash
fly ips list
```

In the Netbeat DNS panel for `3chatbots.com`, add:

| Type  | Host | Value                        |
|-------|------|------------------------------|
| A     | `@`  | _Fly IPv4 from above_        |
| AAAA  | `@`  | _Fly IPv6 from above_        |
| A     | `www`| _Fly IPv4 from above_        |
| AAAA  | `www`| _Fly IPv6 from above_        |

### 6. Issue TLS certificates

Once DNS resolves (a few minutes):

```bash
fly certs add 3chatbots.com
fly certs add www.3chatbots.com
```

Verify:

```bash
curl -I https://www.3chatbots.com/      # expect 302 → /accounts/login/
curl -i  https://www.3chatbots.com/api/health/   # expect {"status":"ok"}
```

---

## Architecture (one-paragraph)

`app/` is a single Django 4.2 project. `chat/` renders the UI from `app/templates/chat/index.html`. `api/` is Django REST Framework, mounted at `/api/`. Browser JS in `app/static/js/main.js` POSTs prompts directly to `/api/prompt/` (same origin, session cookie + CSRF token). `api/services.py:HuggingFaceAPIService` is the integration boundary — it auto-detects demo mode from `HUGGING_FACE_API_TOKEN`. SQLite lives at `app/data/db.sqlite3` (mounted as a Fly volume in production). `LoginRequiredMiddleware` gates everything except `/accounts/`, `/static/`, `/admin/`, `/favicon.ico`, `/api/health/`. Whitenoise serves static files.

## Common operations

```bash
# Local
python app/manage.py migrate
python app/manage.py createsuperuser
python app/manage.py runserver

# Fly.io
fly deploy
fly logs
fly ssh console
fly ssh console -C "python manage.py migrate"
fly ssh console -C "python manage.py createsuperuser"
fly status
fly ips list
fly certs list
```
