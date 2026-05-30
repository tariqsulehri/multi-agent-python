# ─────────────────────────────────────────────────────────
# formatter_agent.py
# ROLE  : The cleaner — formats the combined result
# READS : combined_result, status
# WRITES: combined_result (cleaned), formatted
# RUNS  : fourth in the pipeline (step 4)
# ─────────────────────────────────────────────────────────

from shared_state import state
import re

def run():
    # Safety check — skip if pipeline failed or not ready
    # Accept either approved status or done status
    
    if not state["approved"]:
        print("Formatter ⏸ : no result to format yet, skipping.")
        return  # Exit early

    print("Formatter 🧹 : cleaning up combined result...")

    # Get the combined result from the whiteboard
    raw = state["combined_result"]

    # Remove all markdown bold symbols (**)
    cleaned = raw.replace("**", "")

    # Remove markdown headers (### text → text)
    # re.sub replaces the pattern with just the header text
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)

    # Write the cleaned version back to the whiteboard
    state["combined_result"] = cleaned

    # Mark formatting as done
    state["formatted"] = True

    print("Formatter ✅ : result is clean.")
