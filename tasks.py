import os
import sqlite3
import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "mvp_tracker.db"

class AISubTask(BaseModel):
    task_title: str

class AIGoalBreakdown(BaseModel):
    milestones: list[AISubTask]

# ==============================================================================
# DATABASE STRUCTURAL INITIALIZATION & UPGRADES
# ==============================================================================
def init_db():
    """Initializes tables and dynamically updates schema for timestamping and note storage."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """)
    
    # Updated Schema: Added completed_at and notes text slots
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sub_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            completed_at TEXT,
            notes TEXT,
            FOREIGN KEY (goal_id) REFERENCES goals(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date TEXT UNIQUE
        )
    """)
    
    # SAFE SCHEMA MIGRATION: Injects new columns into old databases if they don't exist
    try:
        cursor.execute("ALTER TABLE sub_tasks ADD COLUMN completed_at TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists, skip cleanly
        
    try:
        cursor.execute("ALTER TABLE sub_tasks ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists, skip cleanly
    
    conn.commit()
    conn.close()


def log_activity():
    """Logs unique calendar dates of app interaction."""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today_str = datetime.date.today().isoformat()
    cursor.execute("INSERT OR IGNORE INTO user_activity (activity_date) VALUES (?)", (today_str,))
    conn.commit()
    conn.close()


def calculate_consistency_stats() -> dict:
    """Analyzes logs to extract total active days and continuous streaks."""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT activity_date FROM user_activity ORDER BY activity_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {"current_streak": 0, "total_active_days": 0}
        
    active_dates = [datetime.date.fromisoformat(row[0]) for row in rows]
    total_active = len(active_dates)
    
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    if active_dates[0] != today and active_dates[0] != yesterday:
        return {"current_streak": 0, "total_active_days": total_active}
        
    streak = 1
    for i in range(len(active_dates) - 1):
        delta = active_dates[i] - active_dates[i+1]
        if delta.days == 1:
            streak += 1
        elif delta.days > 1:
            break
            
    return {"current_streak": streak, "total_active_days": total_active}


# ==============================================================================
# MUTATIONS WITH EXTENDED TELEMETRY FIELDS
# ==============================================================================
def create_new_goal_with_tasks(goal_title: str, tasks_list: list):
    """Saves a parent goal and links its milestones."""
    log_activity()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO goals (title) VALUES (?)", (goal_title,))
    assigned_goal_id = cursor.lastrowid
    
    for task_title in tasks_list:
        cursor.execute(
            "INSERT INTO sub_tasks (goal_id, title) VALUES (?, ?)",
            (assigned_goal_id, task_title)
        )
    conn.commit()
    conn.close()


def get_all_goals() -> list:
    """Fetches goals, pulling timestamps and completion text comments out of SQL."""
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM goals")
    goals_rows = cursor.fetchall()
    
    output = []
    for goal in goals_rows:
        goal_id = goal[0]
        goal_title = goal[1]
        
        # Pull down completed_at and notes columns
        cursor.execute(
            "SELECT id, title, is_completed, completed_at, notes FROM sub_tasks WHERE goal_id = ?", 
            (goal_id,)
        )
        tasks_rows = cursor.fetchall()
        
        formatted_tasks = []
        for task in tasks_rows:
            formatted_tasks.append({
                "task_id": task[0],
                "task_title": task[1],
                "is_completed": bool(task[2]),
                "completed_at": task[3],  # Loaded string metadata
                "notes": task[4]          # Loaded note text
            })
            
        output.append({
            "goal_id": goal_id,
            "goal_title": goal_title,
            "tasks": formatted_tasks
        })
        
    conn.close()
    return output


def update_task_status(task_id: int, is_completed: bool, notes: str = None):
    """Updates status while injecting current time stamps and custom comments."""
    log_activity()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if is_completed:
        # Generate custom precise text representation of time completion
        now_str = datetime.datetime.now().strftime("%b %d, %Y at %I:%M %p")
        cursor.execute(
            "UPDATE sub_tasks SET is_completed = 1, completed_at = ?, notes = ? WHERE id = ?",
            (now_str, notes, task_id)
        )
    else:
        # Clear out metadata if user rolls back completion state
        cursor.execute(
            "UPDATE sub_tasks SET is_completed = 0, completed_at = NULL, notes = NULL WHERE id = ?",
            (task_id,)
        )
        
    conn.commit()
    conn.close()


def generate_ai_tasks(goal_title: str, total_days: int) -> list[str]:
    """Uses Gemini to brainstorm an exact daily step-by-step sequential roadmap."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API Key Missing! Ensure your local .env file contains a valid GEMINI_API_KEY.")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert personal productivity coach. 
    A user has set a large-scale goal: "{goal_title}".
    Break down this big goal into exactly {total_days} sequential, highly actionable daily tasks (1 task per day).
    Each task title must be concise, specific, and clear.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIGoalBreakdown,
            temperature=0.2,
        ),
    )
    
    data = AIGoalBreakdown.model_validate_json(response.text)
    return [item.task_title for item in data.milestones]