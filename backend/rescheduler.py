import sqlite3
from datetime import datetime, timedelta
from scheduler import generate_schedule

DB_PATH = "database/taskflow.db"

def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Normalize dates to always be in the current year (2025)
CURRENT_YEAR = datetime.now().year

def normalize_date(d):
    try:
        dt = datetime.strptime(d, "%Y-%m-%d")
        return dt.replace(year=CURRENT_YEAR).strftime("%Y-%m-%d")
    except:
        return d


def rebuild_week(task_id=None):
    """
    Rebuilds the user's entire schedule.
    If task_id is given → treat it as missed → push it forward 1–3 days.
    """

    conn = db()
    cur = conn.cursor()

    # Fetch all tasks
    cur.execute("SELECT id, task, due_date, estimated_duration FROM tasks")
    rows = cur.fetchall()

    tasks = []
    for r in rows:
        tasks.append({
            "id": r[0],
            "task": r[1],
            "due_date": normalize_date(r[2]),
            "estimated_duration": r[3]
        })

    # If a missed task is specified → push it forward
    if task_id is not None:
        for t in tasks:
            if t["id"] == task_id:
                try:
                    old_date = datetime.strptime(t["due_date"], "%Y-%m-%d")
                    new_date = old_date + timedelta(days=2)  # push forward 2 days
                    t["due_date"] = new_date.strftime("%Y-%m-%d")
                except:
                    pass

    # Save updated due dates back to DB
    for t in tasks:
        cur.execute("""
            UPDATE tasks SET due_date=? WHERE id=?
        """, (t["due_date"], t["id"]))

    conn.commit()
    conn.close()

    # Generate new weekly schedule
    schedule = generate_schedule(tasks)
    return schedule

