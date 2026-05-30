# ─────────────────────────────────────────────────────────
# specialist_pipeline.py
# ─────────────────────────────────────────────────────────
# ROLE  : Runs the 3 specialist agents in sequence
#         with a feedback loop between Writer and Critic
#
# PIPELINE:
#   Step 1 → Researcher  : gathers facts for the task
#   Step 2 → Writer      : turns facts into readable content
#   Step 3 → Critic      : reviews and approves or rejects
#            ↓ if rejected (max 3 retries)
#   Step 2 → Writer      : rewrites with Critic feedback
#   Step 3 → Critic      : reviews again
#            ↓ if approved
#   Step 4 → Save to file
#
# HOW THIS DIFFERS FROM main.py:
#   main.py uses generic Workers with one shared prompt.
#   This pipeline uses specialists with permanent identities.
#   Each agent has a name, role, expertise, and rules.
#   The output is significantly richer and more consistent.
# ─────────────────────────────────────────────────────────

# Import our specialist agents from the agents/ folder
from agents import researcher_agent
from agents import writer_agent
from agents import critic_agent

import os
from datetime import datetime

# Maximum rewrites before accepting the draft
# Prevents infinite loop if Critic is too demanding
MAX_REWRITES = 3

def save_result(task, final_draft):
    # ── Save the approved draft to file ──────────────────
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename  = f"outputs/specialist_{timestamp}.txt"

    with open(filename, "w") as file:
        file.write("TASK\n")
        file.write("─" * 40 + "\n")
        file.write(task + "\n\n")
        file.write("RESULT\n")
        file.write("─" * 40 + "\n")
        file.write(final_draft + "\n\n")
        file.write("PIPELINE\n")
        file.write("─" * 40 + "\n")
        file.write("Researcher → Writer → Critic\n")
        file.write(
            f"Saved at: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    print(f"Saver ✅ : saved to → {filename}")
    return filename

def run():
    print("\n🚀 Starting specialist pipeline...\n")

    # ── Step 1: Get task from user ────────────────────────
    task = input("📝 Enter your task: ").strip()

    if not task:
        print("❌ No task entered.")
        return

    print(f"\nTask set → {task}\n")
    print("─" * 40)

    # ── Step 2: Researcher gathers facts ─────────────────
    # The Researcher thinks like a researcher — not a writer
    # It returns raw factual material for the Writer to use
    research = researcher_agent.run(task)

    print("\n── Research complete. Passing to Writer. ──\n")

    # ── Step 3 + 4: Writer drafts, Critic reviews ────────
    # This loop is Pattern B (feedback loop) combined with
    # Pattern D (specialized identities)
    # Writer and Critic have different identities so their
    # collaboration produces genuinely better output

    draft        = None   # holds the current draft
    rewrite_count = 0     # tracks how many rewrites happened
    feedback     = None   # holds Critic feedback for Writer

    while rewrite_count < MAX_REWRITES:

        # ── Writer drafts (or rewrites with feedback) ────
        if feedback:
            # Rewrite — Writer knows what Critic wants changed
            print(f"\n🔁 Rewrite {rewrite_count} of {MAX_REWRITES}\n")

            # Pass feedback to Writer so it knows what to fix
            write_task = (
                f"{task}\n\n"
                f"Previous draft was rejected by the editor.\n"
                f"Editor feedback: {feedback}\n"
                f"Please rewrite addressing this feedback."
            )
        else:
            # First attempt — just the task and research
            write_task = task

        # Writer produces the draft using the research
        draft = writer_agent.run(write_task, research)

        # ── Critic reviews the draft ──────────────────────
        decision = critic_agent.run(task, draft)

        if decision["approved"]:
            # Critic approved — exit the loop
            print(
                f"\n✅ Draft approved after "
                f"{rewrite_count + 1} attempt(s).\n"
            )
            break

        else:
            # Critic rejected — prepare for rewrite
            feedback      = decision["feedback"]
            rewrite_count += 1

            if rewrite_count > MAX_REWRITES:
                # Hit the limit — accept the current draft
                print(
                    f"\n⚠️  Max rewrites ({MAX_REWRITES}) reached. "
                    f"Accepting current draft.\n"
                )
                break

    # ── Step 5: Save the final approved draft ────────────
    print("─" * 40)
    print("\nFinal result:\n")
    print(draft)
    print("\n" + "─" * 40)

    save_result(task, draft)

    print("\n🎉 Specialist pipeline complete!")
    print(f"   Rewrites taken : {rewrite_count}")

# Run the pipeline when this file is executed directly
if __name__ == "__main__":
    run()