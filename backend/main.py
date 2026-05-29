# ─────────────────────────────────────────────────────────
# main.py
# ROLE  : The entry point — run this file to start everything
#
# Pipeline order:
#   Step 1 → Planner   : YOU type the main task
#   Step 2 → Manager   : judges complexity → routes workers
#   Step 3 → Workers   : run in parallel (1, 2, or 3)
#   Step 4 → Collector : combines all results
#   Step 5 → Reviewer  : approves OR rejects with feedback
#            ↓ if rejected (max 3 retries)
#   Step 3 → Workers   : retry with Reviewer feedback
#   Step 4 → Collector : recombine
#   Step 5 → Reviewer  : check again
#            ↓ if approved (or max retries hit)
#   Step 6 → Formatter : clean the result
#   Step 7 → Saver     : save to file
#
# KEY CONCEPTS:
#   threading.Thread  → runs workers at the same time
#   retry loop        → keeps trying until approved or max retries
#   MAX_RETRIES = 3   → safety limit so it never loops forever
# ─────────────────────────────────────────────────────────

import threading
import worker_agent
import manager_agent
import collector_agent
import formatter_agent
import reviewer_agent
import saver_agent
from shared_state import state

# Maximum number of times Workers can retry before we
# accept the result anyway and move forward
# This prevents an infinite loop if Reviewer is too strict
MAX_RETRIES = 3

def run_workers():
    # ── Launch all Workers in parallel ───────────────────
    # One thread per sub-task — all start at the same time
    # We clear old results first so retry starts fresh

    # Clear previous results before each attempt
    # Without this, old results from last attempt stay in state
    state["results"] = {}

    threads = []
    for index, sub_task in enumerate(state["sub_tasks"]):

        # Create one thread per sub-task
        # target = function to run
        # args   = arguments passed to that function
        # name   = label shown in terminal logs
        thread = threading.Thread(
            target = worker_agent.run,
            args   = (index, sub_task),
            name   = f"Worker-{index + 1}"
        )
        threads.append(thread)
        thread.start()  # start immediately

    # Wait for ALL threads to finish before continuing
    # join() = pause here until this thread is done
    for thread in threads:
        thread.join()

    print("\n✅ All Workers finished.\n")

# ─────────────────────────────────────────────────────────
# MAIN PIPELINE STARTS HERE
# ─────────────────────────────────────────────────────────

print("\n🚀 Starting multi-agent pipeline...\n")

# ── Step 1: Get task from user ───────────────────────────
user_task = input("📝 Enter your main task: ")

# Safety check — do not allow an empty task
if not user_task.strip():
    print("❌ No task entered. Please try again.")
    exit()

# Write the task onto the whiteboard
state["main_task"] = user_task.strip()
print(f"\nPlanner ✅ : main task set → {state['main_task']}\n")

# ── Step 2: Manager judges complexity + creates sub-tasks ─
manager_agent.run()

# Stop if Manager failed — no point continuing
if state["status"] == "error":
    saver_agent.run()
    print("\n❌ Pipeline stopped at Manager step.")
    exit()

# ── Step 3-5: Worker → Collector → Reviewer loop ─────────
# This loop is the feedback pattern (Pattern B)
# It keeps running until:
#   a) Reviewer approves the result, OR
#   b) We hit MAX_RETRIES and accept anyway

print("\n⚡ Launching Workers...\n")

while True:

    # ── Run all Workers in parallel ───────────────────────
    run_workers()

    # ── Collector combines all results ────────────────────
    # We need to reset status to "working" before collecting
    # so Collector knows it should run
    state["status"] = "working"
    collector_agent.run()

    # ── Reviewer checks the combined result ───────────────
    # We set status to "collecting" so Reviewer knows to run
    state["status"] = "collecting"
    reviewer_agent.run()

    # ── Check what Reviewer decided ───────────────────────
    if state["approved"]:
        # Reviewer approved — exit the loop and continue
        print(f"\n✅ Approved after {state['retry_count'] + 1} attempt(s).\n")
        break

    elif state["status"] == "rejected":
        # Reviewer rejected — check if we can retry
        if state["retry_count"] >= MAX_RETRIES:
            # Hit the retry limit — accept the result anyway
            # We never let the pipeline loop forever
            print(
                f"\n⚠️  Max retries ({MAX_RETRIES}) reached. "
                f"Accepting current result.\n"
            )
            state["approved"] = True
            state["status"]   = "approved"
            break

        state["retry_count"] += 1

        # Still within retry limit — tell the user and retry
        print(
            f"\n🔁 Retry {state['retry_count']} of {MAX_RETRIES} "
            f"— Workers improving based on feedback...\n"
        )

    else:
        # Unexpected state — break to avoid infinite loop
        print("⚠️  Unexpected state. Moving forward.")
        break

# ── Step 6: Formatter cleans the result ──────────────────
formatter_agent.run()

# ── Step 7: Saver writes to file ─────────────────────────
saver_agent.run()

# ── Final summary ─────────────────────────────────────────
print("\n" + "─" * 40)
if state["approved"]:
    print("✅  Pipeline completed successfully.")
    print(f"    Complexity    : {state['complexity']}")
    print(f"    Workers used  : {len(state['sub_tasks'])}")
    print(f"    Retries taken : {state['retry_count']}")
    print(f"    Saved to      : outputs/")
elif state["status"] == "error":
    print(f"❌  Pipeline failed → {state['error']}")
else:
    print("⚠️   Pipeline finished in unexpected state.")
print("─" * 40)
