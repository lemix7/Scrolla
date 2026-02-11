# Scrolla

A modern, async social feed API built with FastAPI. Users can register, upload images and videos, browse a personalized feed, and manage their own posts.

---

## Tech Stack

| Layer      | Technology              |
|-----------|-------------------------|
| **Framework** | FastAPI                 |
| **Database**  | SQLite + aiosqlite      |
| **ORM**       | SQLAlchemy (async)      |
| **Auth**      | FastAPI-Users (JWT)     |
| **Media CDN** | ImageKit                |
| **Package Mgmt** | uv                   |

---

## Features

- **Authentication** — JWT-based auth with registration, login, password reset, and email verification
- **Media Upload** — Upload images and videos to ImageKit (stored in the cloud)
- **Feed** — Chronological feed of posts with captions and media
- **Post Management** — Delete your own posts (owner-only)
- **Async** — Fully asynchronous backend for better performance

---

## Prerequisites

- **Python 3.13+**
- **uv** (recommended) — [Install uv](https://docs.astral.sh/uv/)

---

## Setup

### 1. Clone & install

```bash
git clone <repository-url>
cd Scrolla
uv sync
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
SECRET=your-super-secret-jwt-key-change-in-production
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_URL=https://ik.imagekit.io/your-imagekit-id
```

| Variable | Description |
|----------|-------------|
| `SECRET` | Used for JWT signing and password/verification tokens |
| `IMAGEKIT_PRIVATE_KEY` | ImageKit API private key |
| `IMAGEKIT_URL` | ImageKit URL endpoint (from dashboard) |

### 3. Run the server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn app.app:fast_app --host 0.0.0.0 --port 8000 --reload
```

API docs: **http://localhost:8000/docs**

---

## API Overview

### Auth (`/auth`, `/auth/jwt`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/jwt/login` | Login (get JWT) |
| POST | `/auth/jwt/logout` | Logout |
| POST | `/auth/forgot-password` | Request password reset |
| GET | `/auth/verify` | Verify email |
| GET | `/users/me` | Get current user (protected) |

### Posts & Feed

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/upload` | Upload image/video with caption | Required |
| GET | `/feed` | Get all posts (chronological) | Required |
| DELETE | `/posts/{post_id}` | Delete own post | Required |

---

## Project Structure

```
Scrolla/
├── app/
│   ├── app.py      # FastAPI app, routes, lifespan
│   ├── auth.py     # JWT strategy, auth backend
│   ├── db.py       # SQLAlchemy models, engine, session
│   ├── images.py   # ImageKit client
│   ├── schemas.py  # Pydantic schemas
│   └── users.py    # FastAPI-Users config, user manager
├── main.py         # Entry point
├── pyproject.toml  # Dependencies (uv)
└── .env            # Environment variables (create this)
```

---

## Usage Examples

### Register & login

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Login
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret123"
```

### Upload a post

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@/path/to/image.jpg" \
  -F "caption=Hello from Scrolla!"
```

### Get feed

```bash
curl http://localhost:8000/feed \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## License

MIT
