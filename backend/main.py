from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from supabase import create_client
import jwt
from datetime import date

# ── Settings ───────────────────────────────────────────────────────────

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str

    class Config:
        env_file = ".env"

settings = Settings()

# ── App ────────────────────────────────────────────────────────────────

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

# ── Auth ───────────────────────────────────────────────────────────────

def get_user_id(authorization: str) -> str:
    """
    Every request sends a JWT token in the Authorization header.
    This function cracks it open and returns the user's ID.
    """
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ── Models ─────────────────────────────────────────────────────────────

class HabitCreate(BaseModel):
    name: str

# ── Habits ─────────────────────────────────────────────────────────────

@app.get("/habits")
def get_habits(authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    result = supabase.table("habits")\
        .select("*")\
        .eq("user_id", user_id)\
        .execute()
    return result.data


@app.post("/habits", status_code=201)
def create_habit(body: HabitCreate, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    result = supabase.table("habits")\
        .insert({"user_id": user_id, "name": body.name})\
        .execute()
    return result.data[0]


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: str, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    supabase.table("habits")\
        .delete()\
        .eq("id", habit_id)\
        .eq("user_id", user_id)\
        .execute()

# ── Completions ────────────────────────────────────────────────────────

@app.post("/completions/{habit_id}", status_code=201)
def complete_habit(habit_id: str, authorization: str = Header(...)):
    user_id = get_user_id(authorization)

    # Check if already completed today
    existing = supabase.table("completions")\
        .select("id")\
        .eq("habit_id", habit_id)\
        .eq("user_id", user_id)\
        .eq("completed_on", str(date.today()))\
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Already completed today")

    result = supabase.table("completions")\
        .insert({
            "habit_id": habit_id,
            "user_id": user_id,
            "completed_on": str(date.today())
        })\
        .execute()
    return result.data[0]


@app.delete("/completions/{habit_id}", status_code=204)
def uncomplete_habit(habit_id: str, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    supabase.table("completions")\
        .delete()\
        .eq("habit_id", habit_id)\
        .eq("user_id", user_id)\
        .eq("completed_on", str(date.today()))\
        .execute()