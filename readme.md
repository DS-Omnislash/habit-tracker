# 🗓️ Habit Tracker

A full-stack habit tracking app built with FastAPI, Supabase, and vanilla JavaScript.

## What it does

- Log in with email and password
- Create and delete personal habits
- Mark habits as done for today
- Undo today's completion
- Data is private — each user only sees their own habits

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth + JWT |
| Frontend | HTML + CSS + Vanilla JS |

## Project Structure

```
habit-tracker/
├── backend/
│   ├── main.py           # All routes, auth, and config
│   ├── .env              # Secret keys (never commit this)
│   └── requirements.txt  # Python dependencies
├── frontend/
│   └── index.html        # Single-page frontend
└── schema.sql            # Database schema + RLS policies
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/habits` | Get all habits for the logged-in user |
| POST | `/habits` | Create a new habit |
| DELETE | `/habits/{id}` | Delete a habit |
| GET | `/completions` | Get today's completions |
| POST | `/completions/{habit_id}` | Mark a habit as done today |
| DELETE | `/completions/{habit_id}` | Undo today's completion |

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/habit-tracker.git
cd habit-tracker
```

### 2. Set up Supabase

- Create a new project at [supabase.com](https://supabase.com)
- Run `schema.sql` in the Supabase SQL editor
- Copy your project URL and API keys

### 3. Configure the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 4. Run the backend

```bash
uvicorn main:app --reload
```

API will be running at `http://localhost:8000`

### 5. Open the frontend

Open `frontend/index.html` directly in your browser. No build step needed.

## Environment Variables

| Variable | Where to find it |
|----------|-----------------|
| `SUPABASE_URL` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API → anon public |
| `SUPABASE_SERVICE_KEY` | Supabase Dashboard → Settings → API → service_role secret |

> ⚠️ Never commit your `.env` file. The service key has full database access.

## Database Schema

Two tables with a one-to-many relationship:

```
habits        → id, user_id, name, created_at
completions   → id, habit_id, user_id, completed_on
```

Row Level Security (RLS) is enabled on both tables — users can only read and write their own rows.