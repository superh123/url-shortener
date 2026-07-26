# URL Shortener

A full-stack URL shortener built with FastAPI, SQLAlchemy, Redis, and a JavaScript frontend.

## Features

- Create shortened URLs
- Redirect users from short URLs to their original destinations
- Track click statistics:
  - Lifetime clicks
  - Clicks in the last 24 hours
  - Clicks in the last 7 days
  - Clicks in the last 30 days
- Redis-based token bucket rate limiting
- SQLite for local development
- PostgreSQL support for production
- Simple frontend for creating and viewing shortened URLs

## Tech Stack

- **Backend:** FastAPI
- **Database:** SQLAlchemy with SQLite/PostgreSQL
- **Caching & Rate Limiting:** Redis
- **Rate Limiting Algorithm:** Token Bucket
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/shorten` | Create a shortened URL |
| `GET` | `/{code}` | Redirect to the original URL |
| `GET` | `/{code}/stats` | Retrieve click statistics |

## Running Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd url-shortener
```
### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate #For windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Activate Redis server
#### Make sure a Redis server is running locally.

### 5. Start the FastAPI server
```bash
fastapi dev api.py
```
