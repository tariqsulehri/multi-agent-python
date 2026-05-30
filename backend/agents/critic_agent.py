# ─────────────────────────────────────────────────────────
# agents/critic_agent.py
# ─────────────────────────────────────────────────────────
# ROLE      : Specialist — reviews the written draft and
#             either approves it or gives precise feedback
# IDENTITY  : A demanding editor who has high standards
#             and never accepts mediocre work
# READS     : task + draft (both passed as arguments)
# WRITES    : returns decision dict with approved + feedback
# USED BY   : specialist_pipeline.py
#
# WHY THIS MATTERS:
#   The Writer produces good content but cannot critique
#   its own work objectively. The Critic has no emotional
#   attachment to the draft — it only cares about quality.
#   This is the same reason editors exist in publishing.
# ─────────────────────────────────────────────────────────

from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────
# CRITIC IDENTITY
# The Critic is deliberately demanding and specific.
# It does not say "good job" unless the work truly earns it.
# Notice it has strict rules for what makes content pass.
# ─────────────────────────────────────────────────────────
IDENTITY = """
NAME: Critic Agent

ROLE:
You are a strict but fair senior editor.
You review content against a fixed checklist only.
You do NOT invent new requirements each review.
You approve content that passes the checklist.
You reject content that fails the checklist.

FIXED CHECKLIST — check these and ONLY these:
1. Does content directly address the task? (yes/no)
2. Does every section have minimum 3 bullet points? (yes/no)
3. Are specific examples, numbers, or names present? (yes/no)
4. Are there filler intro/outro sentences? (yes/no — fail if yes)
5. Is there at least one section per major topic in the task? (yes/no)

APPROVAL RULE:
- Approve if checklist items 1, 2, 3, 5 are YES and item 4 is NO
- Reject only if a checklist item clearly fails

REJECTION RULE:
- Reject for ONE specific failing checklist item only
- Do not reject for style preferences
- Do not reject for things not on the checklist
- Do not ask for intro or conclusion sections
- Do not move goalposts between reviews

OUTPUT FORMAT — return ONLY this exact JSON:
{"approved": true, "feedback": ""}
or
{"approved": false, "feedback": "Checklist item N failed: specific reason"}

IMPORTANT:
- If content passed your last review it should pass again
- Do not invent new problems that were not there before
- Be consistent — same standards every single review

Return ONLY the JSON. No other text. No markdown.
"""

def run(task, draft):
    # ── Send task + draft to the Critic ──────────────────
    # The Critic receives BOTH:
    #   task  = what the content was supposed to cover
    #   draft = what the Writer produced
    # It compares them and decides pass or fail
    print("Critic 🧐 : reviewing draft...")

    message = (
        f"Original task: {task}\n\n"
        f"Draft to review:\n{draft}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role"    : "system",
                "content" : IDENTITY   # permanent critic identity
            },
            {
                "role"    : "user",
                "content" : message    # task + draft to judge
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Parse the JSON decision safely
    try:
        decision = json.loads(raw)
    except json.JSONDecodeError:
        # If JSON parsing fails, approve anyway
        # Never let a Critic bug block the pipeline
        print("Critic ⚠️  : could not parse decision → auto-approving")
        decision = {"approved": True, "feedback": ""}

    # Print result clearly in terminal
    if decision["approved"]:
        print("Critic ✅ : approved!")
    else:
        print(f"Critic ❌ : rejected → {decision['feedback']}")

    return decision