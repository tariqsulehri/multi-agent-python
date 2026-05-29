# ─────────────────────────────────────────────────────────
# saver_agent.py
# ROLE  : The recorder — saves combined result or error log
# READS : main_task, combined_result, approved, status, error
# WRITES: nothing to shared state — writes to disk only
# RUNS  : last in the pipeline (step 6)
# ─────────────────────────────────────────────────────────

from shared_state import state
import os
from datetime import datetime

def run():
    # Create outputs folder if it does not exist
    os.makedirs("outputs", exist_ok=True)

    # Build unique filename using current timestamp
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    # ── Path A: pipeline succeeded — save the combined result ──
    if state["approved"]:
        filename = f"outputs/result_{timestamp}.txt"
        print("Saver 💾 : saving combined result to file...")

        with open(filename, "w") as file:

            # Section 1 — the original main task
            file.write("MAIN TASK\n")
            file.write("─" * 40 + "\n")
            file.write(state["main_task"] + "\n\n")

            # Section 2 — sub-tasks Manager created
            file.write("SUB-TASKS\n")
            file.write("─" * 40 + "\n")
            for i, task in enumerate(state["sub_tasks"]):
                file.write(f"{i + 1}. {task}\n")
            file.write("\n")

            # Section 3 — the full combined result
            file.write("COMBINED RESULT\n")
            file.write("─" * 40 + "\n")
            file.write(state["combined_result"] + "\n\n")

            # Section 4 — status summary
            file.write("STATUS\n")
            file.write("─" * 40 + "\n")
            file.write(f"Workers used  : {len(state['sub_tasks'])}\n")
            file.write(f"Formatted     : {state['formatted']}\n")
            file.write(f"Approved      : {state['approved']}\n")
            file.write(f"Saved at      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"Saver ✅ : saved to → {filename}")

    # ── Path B: pipeline failed — save error log ──
    elif state["status"] == "error":
        filename = f"outputs/error_{timestamp}.txt"
        print("Saver 💾 : saving error log...")

        with open(filename, "w") as file:
            file.write("MAIN TASK ATTEMPTED\n")
            file.write("─" * 40 + "\n")
            file.write(str(state["main_task"]) + "\n\n")
            file.write("ERROR\n")
            file.write("─" * 40 + "\n")
            file.write(str(state["error"]) + "\n\n")
            file.write("STATUS\n")
            file.write("─" * 40 + "\n")
            file.write(f"Pipeline status : {state['status']}\n")
            file.write(f"Logged at       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"Saver ✅ : error log saved to → {filename}")

    # ── Path C: nothing to save ──
    else:
        print("Saver ⏸ : nothing to save.")