# ⚡ TaskFlow AI — Personal Task Manager

A beautiful, AI-powered personal task manager built with Flask + Google Gemini AI.

## ✨ Features

- **Create & Manage Tasks** — title, description, priority, category, due date
- **🤖 AI Step Breakdown** — Gemini AI breaks any task into clear, actionable steps
- **🤖 AI Productivity Report** — Analyze all your tasks and get focus recommendations
- **Progress Tracking** — Visual progress bar tied to step completion
- **Status Management** — To Do → In Progress → Done
- **Smart Filters** — Filter by status, priority, or overdue
- **Sort Options** — By newest, due date, priority, or progress
- **Search** — Instant full-text search
- **Notes** — Personal notes on each task
- **Stats Dashboard** — Completion rate, priority breakdown, overdue count
- **Keyboard Shortcuts** — `Ctrl+N` new task, `Esc` close modal

## 🚀 Setup

```bash
# 1. Install dependencies
pip install flask

# 2. Run the app
python app.py

# 3. Open browser
# http://localhost:5000
```

## 🔑 Getting a Free Google API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API Key"** (free, no credit card needed)
3. Copy the key
4. When you click any AI feature in the app, paste it in the prompt

Your key is saved in browser localStorage — you only need to enter it once.

## 📁 Structure

```
taskflow/
├── app.py              # Flask backend + Gemini AI proxy
├── templates/
│   └── index.html      # Full UI (HTML + CSS + JS)
├── requirements.txt
├── tasks.json          # Auto-created data file
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | Get all tasks |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/<id>` | Update task |
| DELETE | `/api/tasks/<id>` | Delete task |
| PUT | `/api/tasks/<id>/steps` | Update AI steps |
| GET | `/api/stats` | Get statistics |
| POST | `/api/ai/analyze-task` | Gemini: break task into steps |
| POST | `/api/ai/analyze-all` | Gemini: productivity report |

## 🤖 AI Model Used

**Google Gemini 1.5 Flash** — fast, free tier available, no credit card required.
"# Tak-flow-ai" 
