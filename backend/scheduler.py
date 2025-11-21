import datetime

CURRENT_YEAR = datetime.datetime.now().year

def normalize_date(date_str):
    """Ensure all dates use the current year."""
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return dt.replace(year=CURRENT_YEAR)
    except:
        return None


def generate_schedule(tasks):
    """
    Generate a simple weekly schedule.
    tasks = [
        { "id": 1, "task": "Assignment 1", "due_date": "2025-02-10", "estimated_duration": 2 }
    ]
    """

    # Convert and normalize dates
    for t in tasks:
        t["due_date"] = normalize_date(t["due_date"])

    # Sort tasks by due_date
    tasks = sorted(tasks, key=lambda x: x["due_date"] or datetime.datetime.max)

    # Basic weekly structure
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = {day: [] for day in weekdays}

    # Assign 1hr blocks (simple MVP logic)
    task_index = 0
    HOURS_PER_DAY = 3  # MVP default

    for day in weekdays:
        remaining = HOURS_PER_DAY

        while remaining > 0 and task_index < len(tasks):
            task = tasks[task_index]

            block = {
                "id": task["id"],
                "task": task["task"],
                "due_date": task["due_date"].strftime("%Y-%m-%d") if task["due_date"] else "unknown",
                "hours": 1
            }

            schedule[day].append(block)

            remaining -= 1
            task_index += 1

    return schedule
