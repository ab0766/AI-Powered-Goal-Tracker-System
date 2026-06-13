from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from tasks import (
    create_new_goal_with_tasks, 
    get_all_goals, 
    update_task_status, 
    generate_ai_tasks,
    calculate_consistency_stats
)

app = FastAPI(title="AI-Goal Tracker Core API")

class GoalCreateInput(BaseModel):
    goal_title: str
    generation_mode: str 
    total_days: int = Field(default=7, ge=1, le=30)  
    manual_tasks: list = []

# Extended Data Gateway
class TaskUpdateInput(BaseModel):
    task_id: int
    is_completed: bool
    notes: str = None  # Optional field defaults to None if omitted

@app.get("/")
def home():
    return {"message": "MVP AI-Goal Tracker API is Live and Connected!"}

@app.get("/goals")
def api_get_all_goals():
    return get_all_goals()

@app.get("/user-stats")
def api_get_user_stats():
    return calculate_consistency_stats()

@app.post("/update-task")
def api_update_task(incoming_data: TaskUpdateInput):
    """Processes checkmarks and links completion commentary statements."""
    clean_data = incoming_data.model_dump()
    update_task_status(
        task_id=clean_data["task_id"],
        is_completed=clean_data["is_completed"],
        notes=clean_data["notes"]
    )
    return {"status": "Success", "message": "Updated task status with telemetry records successfully."}

@app.post("/create-goal")
def api_create_goal(incoming_data: GoalCreateInput):
    try:
        clean_data = incoming_data.model_dump()
        title = clean_data["goal_title"]
        mode = clean_data["generation_mode"]
        days = clean_data["total_days"]
        
        final_tasks_to_save = []
        if mode == "ai":
            final_tasks_to_save = generate_ai_tasks(goal_title=title, total_days=days)
        else:
            final_tasks_to_save = clean_data["manual_tasks"]
            
        create_new_goal_with_tasks(goal_title=title, tasks_list=final_tasks_to_save)
        return {"status": "Success", "message": f"Successfully locked in your {days}-day roadmap!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))