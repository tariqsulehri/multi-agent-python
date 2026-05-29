# ─────────────────────────────────────────────────────────
# planner_agent.py
# ROLE  : The manager — decides WHAT needs to be done
# READS : user input from the terminal
# WRITES: task, status
# RUNS  : first in the pipeline (step 1)
# ─────────────────────────────────────────────────────────

# Import the shared whiteboard so we can write the task onto it
from shared_state import state

def run():
    # Ask the user to type their task directly in the terminal
    # input() pauses the program and waits for the user to press Enter
    # The text inside input() is the prompt shown to the user
    user_task = input("📝 Enter your task: ")

    # Safety check — do not allow an empty task
    # .strip() removes accidental spaces before and after the text
    if not user_task.strip():
        # Write error to whiteboard so pipeline skips gracefully
        state["status"] = "error"
        state["error"]  = "No task was entered. Please try again."
        print("Planner ❌ : no task entered.")
        return  # Exit early — do not continue pipeline

    # Write the user's task onto the whiteboard
    state["task"]   = user_task.strip()

    # Update status so Worker knows it is ready to start
    state["status"] = "in_progress"

    # Confirm in terminal so user can see what was captured
    print(f"Planner ✅ : task is set → {state['task']}")