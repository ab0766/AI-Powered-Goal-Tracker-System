import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Goal Architect", page_icon="🎯", layout="centered")

st.title("🎯 AI-Powered Custom Goal Tracking System")

# ==============================================================================
# VISUAL ANALYTICS BANNER: EXTENDED MACRO TARGET DATA TRACKING
# ==============================================================================
# Placeholder initialization variables for metric display processing
streak_val = "0 Days"
active_val = "0 Days"
ongoing_goals_count = 0
achieved_goals_count = 0

try:
    stats_response = requests.get(f"{API_URL}/user-stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        streak_val = f"{stats['current_streak']} Days"
        active_val = f"{stats['total_active_days']} Days"
except Exception:
    pass

# Read goal numbers to calculate large-scale metrics
try:
    goals_response = requests.get(f"{API_URL}/goals")
    if goals_response.status_code == 200:
        all_loaded_goals = goals_response.json()
        for g in all_loaded_goals:
            t = g["tasks"]
            tot = len(t)
            comp = sum(1 for item in t if item["is_completed"])
            if tot > 0 and comp == tot:
                achieved_goals_count += 1
            else:
                ongoing_goals_count += 1
except Exception:
    pass

# Render the upgraded 4-column macro analytics banner
col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    st.metric(label="🔥 App Streak", value=streak_val)
with col_b:
    st.metric(label="📊 Active Days", value=active_val)
with col_c:
    st.metric(label="⏳ Ongoing Goals", value=ongoing_goals_count)
with col_d:
    st.metric(label="🏆 Goals Achieved", value=achieved_goals_count)

st.write("---")

# ==============================================================================
# SECTION 1: HYBRID ROADMAP BUILDER FORM
# ==============================================================================
st.header("🎯 Add Goals to acheive ")

with st.form("dynamic_goal_form", clear_on_submit=False):
    goal_title = st.text_input("What large objective do you want to accomplish?", placeholder="e.g., Master FastAPI Basics")
    total_days = st.slider("How many days do you want this tracking lifecycle to run?", min_value=1, max_value=30, value=7)
    creation_mode = st.radio("How would you like to build out your individual milestones?", options=["Brainstorm via Gemini AI ✨", "Write Manually ✍️"], horizontal=True)
    
    st.write("---")
    manual_input_text = st.text_area("Manual Milestones (Type each milestone step on a brand new line)", placeholder="Day 1: Setup virtual environment\nDay 2: Initialize SQLite")
    submit_button = st.form_submit_button("Generate Day By Day Roadmap & Trackers With AI ✨")

if submit_button:
    if goal_title.strip() == "":
        st.error("❌ A main goal objective title is required!")
    else:
        mode_code = "ai" if "Gemini AI" in creation_mode else "manual"
        payload = {"goal_title": goal_title, "generation_mode": mode_code, "total_days": total_days, "manual_tasks": []}
        
        if mode_code == "manual":
            if manual_input_text.strip() == "":
                st.error("❌ You must input at least one milestone line to save manual entries!")
                st.stop()
            raw_lines = manual_input_text.split("\n")
            payload["manual_tasks"] = [line.strip() for line in raw_lines if line.strip() != ""]
            
        with st.spinner("Executing architecture pipeline operations..."):
            try:
                response = requests.post(f"{API_URL}/create-goal", json=payload)
                if response.status_code == 200:
                    st.success(f"🎉 Success: {response.json()['message']}")
                    st.rerun()
                else:
                    st.error(f"❌ API Error: {response.json().get('detail', 'Internal Server Error')}")
            except Exception as e:
                st.error(f"Failed to communicate with API Network: {e}")

# ==============================================================================
# SECTION 2: MACRO SORTING & MONITORING DISPLAY WITH NOTES ENGINE
# ==============================================================================
st.header("📊 Your Active Trackers")

try:
    response = requests.get(f"{API_URL}/goals")
    
    if response.status_code == 200:
        all_goals = response.json()
        
        if not all_goals:
            st.info("No active goals tracked yet. Use the form above to build one!")
        else:
            ongoing_roadmaps = []
            completed_roadmaps = []
            
            for goal in all_goals:
                tasks = goal["tasks"]
                total_tasks = len(tasks)
                completed_tasks = sum(1 for t in tasks if t["is_completed"])
                
                progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
                goal["calculated_progress"] = progress_percentage
                
                if total_tasks > 0 and completed_tasks == total_tasks:
                    completed_roadmaps.append(goal)
                else:
                    ongoing_roadmaps.append(goal)
            
            # --- DISPLAY A: ONGOING ROADMAPS ---
            st.subheader("⏳ Ongoing Roadmaps")
            if not ongoing_roadmaps:
                st.write("📋 *No ongoing roadmaps.*")
            else:
                for goal in ongoing_roadmaps:
                    with st.expander(f"📋 {goal['goal_title']} ({goal['calculated_progress']}% Done)"):
                        st.write(f"**Goal Tracking ID Reference:** {goal['goal_id']}")
                        st.progress(goal['calculated_progress'] / 100)
                        st.write("---")
                        
                        for task in goal["tasks"]:
                            checkbox_key = f"task_{task['task_id']}"
                            
                            # INTERACTIVE FIELD LOGIC FOR ONGOING TASKS
                            if not task["is_completed"]:
                                is_checked = st.checkbox(task["task_title"], value=False, key=checkbox_key)
                                
                                # Show optional configuration inputs ONLY if ticked true on the interface
                                if is_checked:
                                    note_input = st.text_input(
                                        "📝 Add an optional completion note / reflection:", 
                                        key=f"note_input_{task['task_id']}",
                                        placeholder="e.g., Encountered a minor bug with keys but resolved it."
                                    )
                                    if st.button("Confirm Milestone Done ✅", key=f"confirm_btn_{task['task_id']}"):
                                        requests.post(f"{API_URL}/update-task", json={
                                            "task_id": task["task_id"], 
                                            "is_completed": True,
                                            "notes": note_input.strip() if note_input.strip() else None
                                        })
                                        st.rerun()
                            else:
                                # Reversion checklist logic handling
                                is_checked = st.checkbox(task["task_title"], value=True, key=checkbox_key)
                                if task["completed_at"]:
                                    st.caption(f"⏱️ Done on: {task['completed_at']}")
                                if task["notes"]:
                                    st.info(f"📝 **Note:** {task['notes']}")
                                    
                                if not is_checked:
                                    requests.post(f"{API_URL}/update-task", json={"task_id": task["task_id"], "is_completed": False})
                                    st.rerun()

            st.write("---")

            # --- DISPLAY B: CONQUERED ROADMAPS ---
            st.subheader("✅ Conquered Roadmaps")
            if not completed_roadmaps:
                st.write("🏆 *Finish all daily sub-tasks on a roadmap to move it here!*")
            else:
                for goal in completed_roadmaps:
                    with st.expander(f"🏆 {goal['goal_title']} (100% Complete!)"):
                        st.write(f"**Goal Tracking ID Reference:** {goal['goal_id']}")
                        st.progress(1.0)
                        st.write("---")
                        
                        for task in goal["tasks"]:
                            checkbox_key = f"task_{task['task_id']}"
                            is_checked = st.checkbox(task["task_title"], value=task["is_completed"], key=checkbox_key)
                            
                            # Display historic timestamps and logs saved in database
                            if task["completed_at"]:
                                st.caption(f"⏱️ Finished on: {task['completed_at']}")
                            if task["notes"]:
                                st.info(f"📝 **Reflection Log:** {task['notes']}")
                            
                            if is_checked != task["is_completed"]:
                                requests.post(f"{API_URL}/update-task", json={
                                    "task_id": task["task_id"], 
                                    "is_completed": is_checked
                                })
                                st.rerun()
                                
    else:
        st.error("❌ Core system error: Failed to extract dashboard information.")

except requests.exceptions.ConnectionError:
    st.warning("⚠️ Connection Error: Ensure your FastAPI backend Uvicorn execution loop is fully active.")