import re
import json
import os
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --- Clean text ---
def clean_text(text):
    return text.replace("\n", " ").strip()


# --- Force all dates into the CURRENT YEAR (2025) ---
CURRENT_YEAR = datetime.now().year  # should be 2025 for you


def normalize_date(date_str):
    """
    Convert extracted dates into YYYY-MM-DD format.
    If year is missing → use CURRENT_YEAR.
    If parsing fails → return "unknown".
    """

    if not date_str or date_str.lower() == "unknown":
        return "unknown"

    try:
        # Parse date using dateutil, even if year missing
        parsed = parser.parse(date_str, fuzzy=True, default=datetime(CURRENT_YEAR, 1, 1))

        # Force the year to CURRENT_YEAR
        normalized = parsed.replace(year=CURRENT_YEAR)

        return normalized.strftime("%Y-%m-%d")
    except:
        return "unknown"


def extract_tasks(text):
    text = clean_text(text)

    # ---- Improved prompt that ALWAYS returns stable JSON ----
    prompt = f"""
    Extract ALL academic tasks and deadlines from this text.
    RETURN JSON ONLY. No extra text.

    Schema:
    [
      {{
        "task": "short name of task (e.g., Assignment 2, Final Exam)",
        "due_date": "YYYY-MM-DD or unknown",
        "type": "assignment | quiz | exam | project | misc",
        "estimated_duration_hours": number
      }}
    ]

    - If the task name is missing, infer a brief name from context.
    - If no due date is given, set "unknown".
    - If duration is uncertain, estimate 1–3 hours based on type.
    - ALWAYS return valid JSON.

    TEXT:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content

    # --- Extract JSON safely ---
    try:
        tasks = json.loads(raw)
    except:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            tasks = json.loads(match.group())
        else:
            tasks = []

    # --- Normalize dates so they always use 2025 ---
    for t in tasks:
        if "due_date" in t:
            t["due_date"] = normalize_date(t["due_date"])
        else:
            t["due_date"] = "unknown"

        # Fix missing task titles
        if not t.get("task") or t["task"].strip() == "":
            t["task"] = "Untitled"

        # Ensure duration exists
        if "estimated_duration_hours" not in t or not isinstance(t["estimated_duration_hours"], (int, float)):
            t["estimated_duration_hours"] = 1

    return tasks
