# ─────────────────────────────────────────────────────────
# manager_agent.py
# ROLE  : The brain — reads the task, judges complexity,
#         then creates the right number of sub-tasks
# READS : main_task
# WRITES: complexity, sub_tasks, status
# RUNS  : first in the pipeline (step 1)
#
# NEW — Dynamic routing:
#   Before → always created exactly 3 sub-tasks
#   Now    → judges complexity first, then decides
#             simple  → 1 sub-task  → 1 worker
#             medium  → 2 sub-tasks → 2 workers
#             complex → 3 sub-tasks → 3 workers
# ─────────────────────────────────────────────────────────

from shared_state import state
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────
# COMPLEXITY PROMPT
# First call to OpenAI — just judges how complex the task is
# Returns a single word: simple / medium / complex
# We keep this call separate so the logic is clean and testable
# ─────────────────────────────────────────────────────────
COMPLEXITY_PROMPT = """
You are a task complexity judge.
Read the task and return ONLY one word — nothing else.

Rules:
- "simple"  → a poem, a short answer, one focused topic
- "medium"  → two distinct topics or a comparison task
- "complex" → a full guide, multiple sections, deep research

Return ONLY the word: simple, medium, or complex.
No punctuation. No explanation. Just the word.
"""

# ─────────────────────────────────────────────────────────
# PLANNING PROMPT
# Second call to OpenAI — creates the right number of sub-tasks
# We inject the complexity and task count into the prompt
# so OpenAI knows exactly how many to return
# ─────────────────────────────────────────────────────────
PLANNING_PROMPT = """
You are a task planning assistant.
Break the task into exactly {count} focused sub-tasks.

Rules:
- Return ONLY a JSON array with exactly {count} strings
- Each string is one clear, self-contained sub-task
- No intro sentence, no explanation, no markdown
- Each sub-task must be completable independently

Return ONLY the JSON array. Nothing else.
"""

def judge_complexity():
    # ── Step 1: Ask OpenAI how complex this task is ──
    # We do this as a separate small call before planning
    # so the Manager can make a smart routing decision
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role"    : "system",
                "content" : COMPLEXITY_PROMPT
            },
            {
                "role"    : "user",
                "content" : state["main_task"]
            }
        ]
    )

    # Get the single word back and clean it
    word = response.choices[0].message.content.strip().lower()

    # Validate — must be one of our three expected values
    # If OpenAI returns something unexpected, default to complex
    if word not in ["simple", "medium", "complex"]:
        print(f"Manager ⚠️  : unexpected complexity '{word}' → defaulting to complex")
        word = "complex"

    return word

def create_sub_tasks(count):
    # ── Step 2: Create exactly the right number of sub-tasks ──
    # We inject {count} into the prompt so OpenAI knows
    # exactly how many sub-tasks to return in the JSON array
    prompt = PLANNING_PROMPT.format(count=count)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role"    : "system",
                "content" : prompt
            },
            {
                "role"    : "user",
                "content" : state["main_task"]
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Parse the JSON array safely
    sub_tasks = json.loads(raw)

    # Validate — make sure we got the right number back
    if len(sub_tasks) != count:
        raise ValueError(
            f"Expected {count} sub-tasks, got {len(sub_tasks)}"
        )

    return sub_tasks

def run():
    # Safety check — only run if main task exists
    if not state["main_task"]:
        state["status"] = "error"
        state["error"]  = "No main task found."
        print("Manager ❌ : no main task found.")
        return

    # Update status so we can track where we are
    state["status"] = "planning"
    print("Manager 🧠 : analysing task complexity...")

    try:
        # ── Dynamic routing decision ──────────────────────
        # Step 1: judge complexity
        complexity = judge_complexity()
        state["complexity"] = complexity

        # Map complexity to number of workers needed
        # This is the routing decision — the core of Pattern C
        count_map = {
            "simple"  : 1,   # one worker handles it alone
            "medium"  : 2,   # two workers split the task
            "complex" : 3    # three workers cover it fully
        }
        count = count_map[complexity]

        print(f"Manager 🔍 : complexity → {complexity} ({count} worker(s) needed)")

        # ── Sub-task creation ─────────────────────────────
        # Step 2: create exactly the right number of sub-tasks
        sub_tasks = create_sub_tasks(count)
        state["sub_tasks"] = sub_tasks

        # Update status so Workers know they can start
        state["status"] = "working"

        # Show each sub-task in terminal so you can follow along
        print(f"Manager ✅ : created {count} sub-task(s):")
        for i, task in enumerate(sub_tasks):
            print(f"   {i + 1}. {task}")

    except Exception as e:
        state["error"]  = str(e)
        state["status"] = "error"
        print(f"Manager ❌ : failed → {state['error']}")