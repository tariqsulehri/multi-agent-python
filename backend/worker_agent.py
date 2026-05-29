# ─────────────────────────────────────────────────────────
# worker_agent.py
# ROLE  : The doer — handles one sub-task, writes result
# READS : one sub-task (passed as argument), feedback
# WRITES: results[task_index]
# RUNS  : in parallel — multiple Workers run at same time
#
# NEW — Feedback awareness:
#   Before → Worker only read the sub-task
#   Now    → Worker also reads Reviewer feedback on retry
#            If feedback exists it is added to the prompt
#            so OpenAI knows what to improve
# ─────────────────────────────────────────────────────────

from shared_state import state
from openai import OpenAI
from dotenv import load_dotenv
import threading

load_dotenv()
client = OpenAI()

WORKER_SYSTEM_PROMPT = """
You are a clear and structured writing assistant.
Write focused, informative content for the given topic.

Rules:
- No intro sentence like "Sure!" or "Here is..."
- No outro sentence like "I hope this helps!"
- No markdown bold (**text**)
- Use plain section titles without # symbols
- Under each title add bullet points starting with dash (-)
- Be specific and informative
- Keep response concise and well structured
"""

def run(task_index, sub_task):
    # Get thread name for clear terminal logging
    thread_name = threading.current_thread().name

    # ── Build the message content ─────────────────────────
    # On first attempt: just the sub-task
    # On retry: sub-task + Reviewer feedback
    # This is how the feedback loop works —
    # the Worker improves its answer based on what
    # the Reviewer said was wrong

    if state["feedback"] and state["retry_count"] > 0:
        # Reviewer has given specific feedback
        # We attach it to the task so OpenAI knows what to fix
        message = (
            f"Task: {sub_task}\n\n"
            f"Previous attempt was rejected.\n"
            f"Reviewer feedback: {state['feedback']}\n\n"
            f"Please improve your response based on this feedback."
        )
        print(
            f"Worker {task_index + 1} 🔄 [{thread_name}]: "
            f"retrying with feedback → {state['feedback'][:60]}..."
        )
    else:
        # First attempt — just send the sub-task normally
        message = sub_task
        print(
            f"Worker {task_index + 1} 🔄 [{thread_name}]: "
            f"working on → {sub_task[:50]}..."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role"    : "system",
                    "content" : WORKER_SYSTEM_PROMPT
                },
                {
                    "role"    : "user",
                    "content" : message  # task alone OR task + feedback
                }
            ]
        )

        # Write result to whiteboard under this Worker's index
        state["results"][task_index] = (
            response.choices[0].message.content
        )

        print(f"Worker {task_index + 1} ✅ [{thread_name}]: done.")

    except Exception as e:
        state["results"][task_index] = f"ERROR: {str(e)}"
        print(
            f"Worker {task_index + 1} ❌ [{thread_name}]: "
            f"failed → {str(e)}"
        )