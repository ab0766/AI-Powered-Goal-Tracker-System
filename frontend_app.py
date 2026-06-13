import streamlit as st
import requests

# 1. Page Configuration Branding
st.set_page_config(page_title="Smart Task Manager", layout="centered")
st.title("🎯 Smart Task Manager Dashboard")
st.write("Powered by a FastAPI Backend & Custom Sorting Engine")

FASTAPI_URL = "http://127.0.0.1:8000"

# --- SECTION 1: THE TASK INTAKE FORM (NEW!) ---
st.subheader("➕ Add a New Priority Task")

# st.form bundles inputs together so they only fire when the button is clicked
with st.form("task_input_form", clear_on_submit=True):
    title = st.text_input("Task Title", placeholder="e.g., Study for technical assessment")
    
    # Create side-by-side columns for input sliders and selectors
    col1, col2 = st.columns(2)
    with col1:
        importance = st.slider("Importance Level (1 = Low, 5 = Critical)", 1.0, 5.0, 3.0, step=0.5)
    with col2:
        days_left = st.number_input("Days Left until Deadline", min_value=1, max_value=365, value=3)
        
    submit_button = st.form_submit_button("Optimize & Add Task")

# What happens when the user clicks the submit button
if submit_button:
    if not title.strip():
        st.warning("Please enter a valid task title before submitting.")
    else:
        # Construct the JSON payload to match our backend Pydantic schema exactly
        payload = {
            "title": title,
            "importance": importance,
            "days_left": days_left
        }
        
        try:
            # Ship the data across Port 8000 via an HTTP POST request
            response = requests.post(f"{FASTAPI_URL}/add-task", json=payload)
            
            if response.status_code == 200:
                st.success(f"🚀 Success: {response.json().get('message')}")
            else:
                st.error(f"Validation Error ({response.status_code}): Could not save task.")
                
        except requests.exceptions.ConnectionError:
            st.error("Network Error: Make sure your Uvicorn backend server is running on Port 8000!")


# --- SECTION 2: DISPLAY SORTED TASKS ---
st.markdown("---")
st.subheader("📋 Current Priority Standings")

try:
    response = requests.get(f"{FASTAPI_URL}/tasks")
    if response.status_code == 200:
        tasks = response.json()
        if not tasks:
            st.info("Your priority backlog is completely clear!")
        else:
            st.dataframe(tasks, use_container_width=True)
    else:
        st.error("Error fetching tasks from backend.")
except requests.exceptions.ConnectionError:
    st.error("Could not render data table. Backend server is offline.")