# 21MAN_back

KHU 21MAN backend repository.

## Stack

- Python 3.11+
- FastAPI
- Uvicorn

## Getting Started

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Server runs at:

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/v1/health

## Project Structure

```text
app/
  api/
    routes/
      health.py
  core/
    config.py
  main.py
```
