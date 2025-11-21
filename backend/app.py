from flask import Flask, request, jsonify
from flask_cors import CORS
from extractor import extract_tasks
from datetime import datetime, timedelta

app = Flask(__name__, static_url_path='/frontend', static_folder='frontend')
CORS(app)


# -------------------------
# ROUTE: Backend Test
# -------------------------
@app.route("/")
def home():
    return jsonify({"message": "TaskFlow backend running"})


# -------------------------
# ROUTE: Extract Tasks
# -------------------------
@app.route("/extract_deadlines", methods=["POST"])
def extract_deadlines():
    data = request.get_json()
    text = data.get("text", "")

    tasks = extract_tasks(text)

    return jsonify({"tasks": tasks})


# -------------------------
# ROUTE: Auto Schedule Builder
# -------------------------
@app.route("/generate_schedule", methods=["POST"])
def generate_schedule():
    """
    Input:
    {
      "tasks": [...],
      "hours_per_day": 3,
      "availability": ["Mon","Tue","Wed","Thu","Fri"]
    }
    """

    data = request.get_json()

    tasks = data.get("tasks", [])
    hours_per_day = data.get("hours_per_day", 3)
    availability = data.get("availability", ["Mon", "Tue", "Wed", "Thu", "Fri"])

    # WEEK structure
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    schedule = {day: [] for day in week_days}

    # STEP 1 — Sort tasks by due date
    def sort_key(task):
        d = task.get("due_date", "unknown")
        if d == "unknown":
            return datetime(2099, 1, 1)
        return datetime.strptime(d, "%Y-%m-%d")

    tasks = sorted(tasks, key=sort_key)

    # STEP 2 — Distribute tasks across the week
    day_pointer = 0  # start at Monday

    for task in tasks:
        duration = task.get("estimated_duration_hours", 1)

        hours_left = duration

        while hours_left > 0:
            current_day = week_days[day_pointer % 7]

            # If student is unavailable that day → skip
            if current_day not in availability:
                day_pointer += 1
                continue

            # Add one hour block
            schedule[current_day].append({
                "task": task.get("task", "Untitled"),
                "due_date": task.get("due_date", "unknown"),
                "hours": 1
            })

            hours_left -= 1
            day_pointer += 1

    return jsonify({"schedule": schedule})


# -------------------------
# ROUTE: Serve Frontend Files
# -------------------------
@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(debug=True)



