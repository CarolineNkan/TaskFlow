# backend/app.py

from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import traceback

from scheduler import generate_schedule
from extractor import extract_tasks
from rescheduler import rebuild_week

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "taskflow.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def root():
    return {"message": "TaskFlow backend running"}


# --------------------------------------------
# FRONTEND FILE SERVING
# --------------------------------------------
FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    return send_from_directory(FRONTEND_FOLDER, filename)



# =====================================================
# 1. GET TASKS (needed for dashboard)
# =====================================================
@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    tasks = [dict(r) for r in rows]
    return jsonify({"tasks": tasks})



# =====================================================
# 2. EXTRACT DEADLINES
# =====================================================
@app.route("/extract_deadlines", methods=["POST"])
def extract_deadlines():
    try:
        data = request.get_json()
        text = data.get("text", "")

        tasks = extract_tasks(text)

        conn = get_db()
        cursor = conn.cursor()

        for t in tasks:
            cursor.execute(
                """
                INSERT INTO tasks (task, due_date, type, estimated_duration)
                VALUES (?, ?, ?, ?)
                """,
                (
                    t.get("task", "Untitled"),
                    t.get("due_date", "unknown"),
                    t.get("type", "misc"),
                    t.get("estimated_duration_hours", 1),
                ),
            )

        conn.commit()
        conn.close()

        return jsonify({"tasks": tasks})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# =====================================================
# 3. GENERATE WEEKLY SCHEDULE
# =====================================================
@app.route("/generate_schedule", methods=["POST"])
def generate_schedule_route():

    conn = get_db()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    tasks = [dict(r) for r in rows]

    schedule = generate_schedule(tasks)
    return jsonify({"schedule": schedule})



# =====================================================
# 4. RESCHEDULER (MISSED TASK)
# =====================================================
@app.route("/rebuild_week", methods=["POST"])
def rebuild_week_route():
    try:
        data = request.get_json()
        task_id = data.get("task_id")

        schedule = rebuild_week(task_id)
        return jsonify({"schedule": schedule})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# =====================================================
# START SERVER
# =====================================================
if __name__ == "__main__":
    print("Running TaskFlow backend...")
    print("DB =", DB_PATH)
    app.run(debug=True)
