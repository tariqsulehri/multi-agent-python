# ─────────────────────────────────────────────────────────
# collector_agent.py
# ROLE  : The combiner — joins all Worker results into one
# READS : sub_tasks, results, status
# WRITES: combined_result, status
# RUNS  : after all Workers finish (step 3)
#
# HOW IT WORKS:
#   Loops through all results in order (0, 1, 2),
#   adds the original sub-task as a section header,
#   and joins everything into one clean text block.
# ─────────────────────────────────────────────────────────

# Import the shared whiteboard
from shared_state import state

def run():
    # Safety check — only collect if Workers have finished
    if state["status"] != "working":
        print("Collector ⏸ : workers not done yet, skipping.")
        return  # Exit early

    # Safety check — make sure we actually have results to collect
    if not state["results"]:
        state["status"] = "error"
        state["error"]  = "No results found from Workers."
        print("Collector ❌ : no results to collect.")
        return  # Exit early

    print("Collector 📦 : combining all results...")

    # This list will hold all sections as we build the combined output
    combined_sections = []

    # Loop through results in order (0, 1, 2)
    # sorted() makes sure we always combine in the correct order
    for index in sorted(state["results"].keys()):

        # Get the original sub-task title for this result
        # This becomes the section header in the combined output
        sub_task = state["sub_tasks"][index]

        # Get the result this Worker produced
        result = state["results"][index]

        # Build one section: title + content
        # We add a blank line after each section for readability
        section = f"{sub_task}\n{'─' * 40}\n{result}"

        # Add this section to our combined list
        combined_sections.append(section)

        print(f"Collector ✅ : collected result {index + 1} of {len(state['results'])}")

    # Join all sections with double line breaks between them
    state["combined_result"] = "\n\n".join(combined_sections)

    # Update status so Formatter knows it can start
    state["status"] = "done"

    print("Collector ✅ : all results combined.")