# 🎯 SprintMap AI: AI-Powered Custom Goal Tracking System Architect

SprintMap AI is a production-ready, full-stack productivity tool that shifts away from typical manual micro-management tracking applications. Built using a decoupling architecture, it blends a high-performance **FastAPI asynchronous backend** with an interactive **Streamlit frontend engine** to break down massive monthly ambitions into day-by-day micro-milestones using **Google Gemini AI**.

---

## 🚀 Core Value Proposition
When taking on large engineering or personal objectives, cognitive overwhelm often causes early burnouts. SprintMap AI forces a hard constraint layout: 
* **Macro Destination:** You choose your large high-level target.
* **Time Constraint:** You limit execution tracking to a strict timeline (up to 30 days maximum).
* **Hybrid Blueprints:** The application leverages GenAI to systematically map your exact requirement for every single day or gives you complete manual design flexibility.

---

## 🛠️ Tech Stack & Architecture Matrix

| Layer | Technology | Primary Functionality |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive visual state dashboard & interaction panel |
| **Backend API** | FastAPI | High-performance RESTful API gateway & server pipeline |
| **GenAI Brain** | Google GenAI SDK (`gemini-2.5-flash`) | AI agent orchestration utilizing structured JSON schema outputs |
| **Validation Layer** | Pydantic v2 | Enforces type constraints & deep integrity parsing at network entry |
| **Database Sheet** | SQLite | Relational schema storage with safe transaction controls |

---

## ✨ Features Breakdown

* **Dynamic Analytics Banner:** Real-time generation of continuity metrics, tracking daily app engagement streaks, active login accumulation, and macro-level goal statuses.
* **Automated Goal Sorting Engine:** The frontend evaluates milestone records and splits entire roadmap project cards into separate `⏳ Ongoing Roadmaps` and `✅ Conquered Roadmaps` display sections.
* **AI Structured Outputs:** Leverages Gemini's schema configuration controls to guarantee the LLM communicates strictly via structured JSON arrays mapped directly to internal Pydantic models.
* **Historic Telemetry Logs:** Automatically injects clean completion timestamps into the relational data layers when checking off tasks.
* **Daily Reflection Notes:** Opens dynamic nested text fields right on the checklist interface to save optional progress journal thoughts, keeping a rich history of adjustments.

---

## 🗄️ Relational Database Layout

The local file database (`mvp_tracker.db`) uses a clean **One-to-Many relational architecture**:

```text
  ┌───────────────┐          ┌──────────────────────────────────────────────┐
  │   GOALS       │          │   SUB_TASKS                                  │
  ├───────────────┤          ├──────────────────────────────────────────────┤
  │ id (PK)       │───┐      │ id (PK)                                      │
  │ title         │   └─────►│ goal_id (FK)                                 │
  └───────────────┘          │ title                                        │
                             │ is_completed (0 or 1)                        │
                             │ completed_at (TIMESTAMP TEXT)                │
                             │ notes (TEXT)                                 │
                             └──────────────────────────────────────────────┘
```
## Quickstart Installation Guide

### 1. Clone the Workspace
```bash
git clone [https://github.com/your-username/SprintMap-AI.git](https://github.com/your-username/SprintMap-AI.git)
cd SprintMap-AI
```
### 2. Configure Virtual Environment & Dependencies
```bash
# Initialize isolated environment
python -m venv venv

# Activate workspace environment (Windows)
venv\Scripts\activate

# Activate workspace environment (Mac/Linux)
source venv/bin/activate

# Install required core packages
pip install -r requirements.txt

Once loaded, navigate your local browser to `http://localhost:8501` to use the application!
```

### 3. Establish Private API Key Security Gateway
```bash
LLM_API_KEY=your_actual__api_key_here
```
### 4. Fire Up the Server Execution Loops
* **Terminal 1 (Run the FastAPI Core Backend Layer):**

```bash
uvicorn app:app --reload
```
* **Terminal 2 (Run the Streamlit Graphical Dashboard Interface):**
```bash
    streamlit run dashboard.py
```

Once loaded, navigate your local browser to `http://localhost:8501` to use the application!

---

## 📄 License
Distributed under the **MIT License**. This grant allows unrestricted open-source development, modification, and deployment flexibility. See the `LICENSE` document file for details.

---

## 👤 Author
**Abhishek Biswas**  
* **LinkedIn:** [www.linkedin.com/in/abhishekbiswas07](https://linkedin.com)  
* **GitHub:** [github.com/ab0766](https://github.com)
