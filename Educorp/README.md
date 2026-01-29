# EduCorp - The Agentic Internship Simulator
dilshad
**EduCorp** is a next-generation EdTech platform that bridges the gap between passive learning and corporate reality. It combines a **Dynamic Learning Roadmap** with a high-fidelity **Virtual Internship Simulator** powered by autonomous AI agents.

---

## 🚀 Key Features

### 1. 🏢 Virtual Internship Simulator (The "OS")
A browser-based Operating System that simulates a real software engineering job.
*   **Virtual Desktop**: Built with a "Window Manager" interface (Draggable windows, Taskbar).
*   **AI Manager ("Alice")**: An autonomous agent that assigns tasks, reviews your code, and evaluates your **Trust Score**.
    *   *Ruthless Reliability*: Bad code or rude emails lower your trust score (-10).
    *   *Promotions*: High trust scores unlock better projects.
*   **Integrated Tools**:
    *   **Email Client**: Receive tasks and communicate with stakeholders.
    *   **VS Code-style IDE**: Write and execute Python code in-browser (with Tab completion & syntax highlighting).
    *   **Kanban Board**: Drag-and-drop task management.

### 2. 🧠 Agentic Learning Planner
An intelligent curriculum generator that adapts to your skill level.
*   **Dynamic Roadmaps**: Generates visual learning graphs based on any topic.
*   **Generative Widgets**: Click any node (e.g., "Sorting Algorithms") to generate a **Explorable Explanation**.
    *   *Visual Engines*: The AI writes HTML/JS on the fly to build (1) Sorting Visualizers, (2) Graph Demos, or (3) Flow Simulations.
    *   *Tech*: Uses **Tailwind CSS** + Vanilla JS for high-performance widgets.

### 3. 🤖 AI Mock Interviewer
*   **Multi-Persona**: Switch between "Friendly HR", "Technical Team Lead", or "System Design Expert".
*   **Real-time Feedback**: Get instant grading on your answers.

---

## 🛠️ Tech Stack

### Frontend
*   **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
*   **Styling**: [Tailwind CSS](https://tailwindcss.com/)
*   **Fonts**: Outfit (Sans) + JetBrains Mono (Code)
*   **Icons**: Lucide React
*   **State**: React Flow (for Roadmaps)

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **AI Engine**: [Groq](https://groq.com/) (Running **Llama-3.3-70b-versatile**) for extreme speed.
*   **Agent framework**: Custom Agent Loop + LangChain.
*   **Database**: MongoDB (Local).
*   **Search**: Tavily API (for real-world resource fetching).

---

## ⚡ Getting Started

### Prerequisites
1.  **Node.js** (v18+)
2.  **Python** (v3.10+)
3.  **MongoDB** running locally on port `27017`.

### 1. Backend Setup
Navigate to the backend folder and start the server.

```powershell
cd backend

# Create Virtual Env (Recommended)
python -m venv venv
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_key_here > .env
echo TAVILY_API_KEY=your_key_here >> .env

# Run Server (or use run_server.bat)
python -m uvicorn app.main:app --reload --port 8000
```
*Server will start at `http://localhost:8000`*

### 2. Frontend Setup
Navigate to the frontend folder.

```powershell
cd frontend

# Install Dependencies
npm install

# Run Development Server
npm run dev
```
*App will start at `http://localhost:3000`*

---

## 🎮 How to Play (Internship Mode)

1.  Open `http://localhost:3000/educorp`.
2.  Click **"Begin Internship"**.
3.  Wait for **Manager Alice** to send you a Welcome Email.
4.  **Read the Task**: Check your Inbox for the project brief.
5.  **Write Code**: Open the **IDE**, write the solution (e.g., a Python script).
6.  **Submit**: Click the floating "Run Code" button.
7.  **Survive**: Monitor your **Trust Score** in the sidebar. If it drops below 40%, you're in trouble!

---

## 📂 Project Structure

```
D:\hackved\
├── backend\
│   ├── app\
│   │   ├── services\      # Agent Logic (manager_agent, planner_agent)
│   │   ├── main.py        # API Routes
│   │   └── models.py      # Pydantic Schemas
│   └── requirements.txt
├── frontend\
│   ├── src\
│   │   ├── components\    # Shared UI (PlannerDashboard, WidgetModal)
│   │   ├── app\educorp\   # Internship Simulator Pages
│   │   └── lib\           # Utils
│   └── tailwind.config.ts
└── README.md
```

---

*Powered by Agentic AI. Built for the Future of Work.*
