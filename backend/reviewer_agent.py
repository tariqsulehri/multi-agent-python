# ─────────────────────────────────────────────────────────
# reviewer_agent.py
# ROLE  : The quality checker — reads result and decides
#         to approve OR reject with specific feedback
# READS : combined_result, status, retry_count
# WRITES: approved, feedback, status
# RUNS  : after Collector (step 5) and after each retry
#
# NEW — Feedback loop:
#   Before → Reviewer only approved, never rejected
#   Now    → Reviewer can reject and write specific feedback
#            Worker reads that feedback and improves
#            Max 3 retries before pipeline accepts anyway
# ─────────────────────────────────────────────────────────

from shared_state import state
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────
# REVIEWER SYSTEM PROMPT
# Tells OpenAI to act as a strict quality checker
# Returns a JSON object with two fields:
#   approved : true or false
#   feedback : empty string if approved,
#              specific feedback if rejected
# We use JSON so we can parse the decision reliably
# ─────────────────────────────────────────────────────────
REVIEWER_SYSTEM_PROMPT = """
You are a strict quality reviewer for AI-generated content.

Review the content and return ONLY a JSON object.

If the content is good quality, return:
{"approved": true, "feedback": ""}

If the content needs improvement, return:
{"approved": false, "feedback": "your specific feedback here"}

Quality standards — reject if ANY of these are true:
- Content is too vague or generic (no specific details)
- Missing important sections for the topic
- Has intro/outro filler sentences
- Sections are too short (under 3 bullet points each)
- Content does not directly address the task

Feedback rules when rejecting:
- Be specific about what exactly needs to improve
- Reference the actual section or content that is weak
- Keep feedback under 2 sentences
- Be constructive, not just critical

Return ONLY the JSON object. No other text.
"""

def run():
    # Safety check — only review if content is ready
    if state["status"] not in ["collecting", "done"]:
        print("Reviewer ⏸ : result not ready, skipping.")
        return

    print(f"Reviewer 🔍 : checking result (attempt {state['retry_count'] + 1} of 3)...")

    try:
        # Ask OpenAI to review the combined result
        # We pass the entire combined result for review
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role"    : "system",
                    "content" : REVIEWER_SYSTEM_PROMPT
                },
                {
                    "role"    : "user",
                    "content" : (
                        f"Task: {state['main_task']}\n\n"
                        f"Content to review:\n{state['combined_result']}"
                    )
                }
            ]
        )

        # Parse the JSON decision from Reviewer
        import json
        raw      = response.choices[0].message.content.strip()
        decision = json.loads(raw)

        if decision["approved"]:
            # ── Reviewer approved ─────────────────────────
            state["approved"] = True
            state["status"]   = "approved"
            state["feedback"] = None  # clear any old feedback

            # Print the result for you to see in terminal
            print("\n" + "─" * 40)
            print(state["combined_result"])
            print("─" * 40)
            print("\nReviewer ✅ : approved!")

        else:
            # ── Reviewer rejected ─────────────────────────
            # Write the feedback onto the whiteboard
            # Workers will read this on their next attempt
            state["feedback"] = decision["feedback"]
            state["status"]   = "rejected"

            print(
                f"Reviewer ❌ : rejected → {decision['feedback']}"
            )

    except Exception as e:
        # If Reviewer itself fails, approve anyway
        # We never let a Reviewer crash stop the pipeline
        print(f"Reviewer ⚠️  : review failed ({str(e)}) → auto-approving")
        state["approved"] = True
        state["status"]   = "approved"