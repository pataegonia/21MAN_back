# 21MAN_back

KHU 21MAN backend repository.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- MySQL
- SQLAlchemy 2.0
- Alembic
- Email / Password / JWT auth

## Getting Started

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

**WSL / Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Server runs at:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/v1/health

## Environment

Local environment variables live in `.env`.

Important values:

```env
APP_DEBUG=true
DATABASE_URL=mysql+pymysql://worldbuild:worldbuild@localhost:3306/worldbuild
JWT_SECRET=dev-change-this-jwt-secret-at-least-32-bytes
JWT_ALGORITHM=HS256
JWT_ISSUER=worldbuild
JWT_AUDIENCE=worldbuild-api
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=14
BCRYPT_ROUNDS=12
IP_HASH_SECRET=dev-change-this-ip-secret-at-least-32-bytes
OPENAI_API_KEY=
```

`DEBUG` is intentionally not used because it often conflicts with system or shell-level variables.

## Auth

MVP auth uses JWT access tokens and opaque refresh tokens.

- Access token: JWT HS256, 30 minutes
- Refresh token: random opaque token, 14 days
- Refresh tokens are stored only as SHA-256 hashes
- Refresh rotates on every `/auth/refresh`
- Reusing a revoked refresh token revokes the whole token family

Endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

## Database

DB infrastructure can be added later. Once MySQL is ready and `DATABASE_URL` points to it:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Project Structure

```text
app/
  api/
    router.py
    routes/
      health.py
  core/
    config.py
    exceptions.py
  db/
    base.py
    base_class.py
    session.py
  models/
    ai_analysis.py
    audit_log.py
    enums.py
    merge.py
    notification.py
    pull_request.py
    refresh_token.py
    repository.py
    user.py
  repositories/
  schemas/
  services/
  main.py
alembic/
```
