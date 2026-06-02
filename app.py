from flask import Flask, request, jsonify, render_template
import json
import os
import uuid
from datetime import datetime
import google.generativeai as genai
app = Flask(__name__)
TASKS_FILE = "tasks.json"
# File Helpers
def load_tasks():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []
def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)
# Gemini Helper
def call_gemini(api_key, prompt):
    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1200
            }
        )

        return response.text

    except Exception as e:
        print("Gemini Error:", str(e))
        raise Exception(str(e))
# Routes
@app.route("/")
def index():
    return render_template("index.html")
# Task CRUD
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks())
@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.json
    tasks = load_tasks()
    task = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "priority": data.get("priority", "medium"),
        "category": data.get("category", "general"),
        "due_date": data.get("due_date", ""),
        "status": "todo",
        "steps": [],
        "tags": data.get("tags", []),
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "ai_analysis": None,
        "progress": 0,
        "notes": ""
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify(task), 201
@app.route("/api/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task.update(data)
            if (
                data.get("status") == "done"
                and not task.get("completed_at")
            ):
                task["completed_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404
@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return jsonify({"success": True})
@app.route("/api/tasks/<task_id>/steps", methods=["PUT"])
def update_steps(task_id):
    data = request.json
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["steps"] = data.get("steps", [])
            completed = sum(
                1 for step in task["steps"]
                if step.get("done")
            )
            total = len(task["steps"])
            task["progress"] = (
                int((completed / total) * 100)
                if total > 0
                else 0
            )
            save_tasks(tasks)
            return jsonify(task)
    return jsonify({"error": "Task not found"}), 404
# Statistics

@app.route("/api/stats", methods=["GET"])
def get_stats():

    tasks = load_tasks()

    total = len(tasks)

    done = sum(
        1 for t in tasks
        if t["status"] == "done"
    )

    in_progress = sum(
        1 for t in tasks
        if t["status"] == "in_progress"
    )

    todo = sum(
        1 for t in tasks
        if t["status"] == "todo"
    )

    overdue = 0

    today = datetime.now().date()

    for task in tasks:

        if task.get("due_date") and task["status"] != "done":

            try:
                due_date = datetime.fromisoformat(
                    task["due_date"]
                ).date()

                if due_date < today:
                    overdue += 1

            except:
                pass

    by_priority = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    by_category = {}

    for task in tasks:

        priority = task.get("priority", "medium")

        if priority in by_priority:
            by_priority[priority] += 1

        category = task.get("category", "general")

        by_category[category] = (
            by_category.get(category, 0) + 1
        )

    completion_rate = (
        round(done / total * 100)
        if total
        else 0
    )

    return jsonify({
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "todo": todo,
        "overdue": overdue,
        "by_priority": by_priority,
        "by_category": by_category,
        "completion_rate": completion_rate
    })


# -------------------------------
# AI Analyze Single Task
# -------------------------------

@app.route("/api/ai/analyze-task", methods=["POST"])
def ai_analyze_task():

    data = request.json

    task = data.get("task", {})
    context = data.get("context", "")
    api_key = data.get("api_key", "")

    if not api_key:
        return jsonify({
            "error": "Google API key is required"
        }), 400

    prompt = f"""
You are a productivity AI.

Task: {task.get('title', '')}
Description: {task.get('description', '')}
Priority: {task.get('priority', 'medium')}
Category: {task.get('category', 'general')}
Context: {context}

Return ONLY valid JSON.

Format:
[
  {{
    "insight": "short productivity insight"
  }},
  {{
    "text": "step 1",
    "done": false
  }}
]

Generate 5-8 actionable steps.

No markdown.
No explanations.
"""

    try:

        raw = call_gemini(api_key, prompt)

        print("\n=== GEMINI RESPONSE ===")
        print(raw)

        clean = (
            raw.replace("```json", "")
               .replace("```", "")
               .strip()
        )

        start = clean.find("[")
        end = clean.rfind("]") + 1

        if start != -1 and end > start:
            clean = clean[start:end]

        parsed = json.loads(clean)

        insight = ""
        steps = []

        for item in parsed:

            if "insight" in item:
                insight = item["insight"]

            elif "text" in item:
                steps.append({
                    "text": item["text"],
                    "done": False
                })

        return jsonify({
            "steps": steps,
            "insight": insight
        })

    except json.JSONDecodeError:

        return jsonify({
            "error": "Failed to parse Gemini JSON response",
            "raw_response": raw
        }), 500

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -------------------------------
# AI Analyze All Tasks
# -------------------------------

@app.route("/api/ai/analyze-all", methods=["POST"])
def ai_analyze_all():

    data = request.json

    tasks_list = data.get("tasks", [])
    api_key = data.get("api_key", "")

    if not api_key:
        return jsonify({
            "error": "Google API key is required"
        }), 400

    pending = [
        task for task in tasks_list
        if task.get("status") != "done"
    ][:15]

    if not pending:
        return jsonify({
            "report": "No pending tasks found."
        })

    task_text = "\n".join(
        f"- {t.get('title')} | "
        f"Priority: {t.get('priority')} | "
        f"Status: {t.get('status')}"
        for t in pending
    )

    prompt = f"""
You are an expert productivity coach.

Analyze these tasks:

{task_text}

Provide:

1. Top 3 priorities
2. Suggested schedule
3. Productivity tips
4. One motivational message

Use emojis.
Keep it concise.
"""

    try:

        report = call_gemini(api_key, prompt)

        return jsonify({
            "report": report
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -------------------------------
# Main
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=500)
