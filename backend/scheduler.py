# backend/scheduler.py

import datetime


def build_schedule(tasks, availability, hours_per_day):
    """
    tasks: list[dict] from DB or extractor
    availability: { "Mon": True, "Tue": True, ... }
    hours_per_day: int (user preference)
    """

    # Convert to datetime objects
    for t in tasks:
        try:
            t["due_date"] = datetime.datetime.strptime(t["due_date"], "%Y-%m-%d")
        except:
            t["due_date"] = None

    # Sort tasks by due date (soonest first)
    tasks = sorted(tasks, key=lambda x: x["due_date"] or datetime.datetime.max)

    # Build schedule object
    schedule = {day: [] for day in availability.keys()}

    # Distribute hours
    task_index = 0

    for day, is_available in availability.items():
        if not is_available:
            continue

        remaining_hours = hours_per_day

        while remaining_hours > 0 and task_index < len(tasks):
            task = tasks[task_index]

            block = {
                "task": task.get("title", "Untitled"),
                "due_date": task.get("due_date").strftime("%Y-%m-%d")
                    if task.get("due_date") else "unknown",
                "allocated": 1  # 1 hour block
            }

            schedule[day].append(block)

            remaining_hours -= 1
            task_index += 1

    return schedule
