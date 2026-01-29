# NEONHIRE (Clean)

A minimal FastAPI + SQLite demo app with registration, login (JWT), and a protected "Me" endpoint. Includes EN/RU language toggle and Jinja2 pages for a freelance marketplace demo.

## Features

- Registration and login with SQLite
- JWT auth with `/api/auth/me`
- Jinja2 pages for Home, Jobs, Freelancers, Profile
- EN/RU language toggle via cookie
- Works on Windows + Python 3.13

## Quick start (Windows-friendly)

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Open the app**
   - http://127.0.0.1:8000

## How to run (10-step checklist)

1. Clone the repository.
2. Open a terminal and change into the project directory.
3. Create a virtual environment: `python -m venv .venv`.
4. Activate it on Windows: `.venv\\Scripts\\activate`.
5. Install dependencies: `pip install -r requirements.txt`.
6. (Optional) Set `SECRET_KEY` in your environment or `.env`.
7. Start the server: `uvicorn app.main:app --reload`.
8. Open `http://127.0.0.1:8000/register`.
9. Register a new account.
10. Log in at `/login` and confirm the home page shows your email.

## Demo flow (freelance marketplace)

1. Register a new user at `/register`.
2. Log in at `/login`.
3. Open `/jobs/new` and create a job post.
4. Open `/freelancers/new` and create a freelancer profile.
5. Visit `/jobs` and `/freelancers` to confirm lists.
6. Open `/profile` for quick links.
7. Click **Log out** to clear the session cookie.

## Manual verification checklist

- `pip install -r requirements.txt` works on Windows Python 3.13
- `uvicorn app.main:app --reload` starts
- `/register` creates user in `app.db`
- After registration, UI shows success message and redirects to `/login`
- `/login` returns token; home page shows user email
- `/jobs/new` and `/freelancers/new` create records and redirect with success message
- `/jobs` and `/freelancers` list newest items first
- RU/EN toggle changes text; no console errors
- `GET /api/auth/me` returns current user with Authorization header

## API examples

Register:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secret"}'
```

Login:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secret"}'
```

Me:
```bash
curl http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
```

## Password handling (bcrypt + SHA-256 prehash)

Passwords are SHA-256 pre-hashed before bcrypt, enabling unlimited length inputs while keeping bcrypt compatibility.
