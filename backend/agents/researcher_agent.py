"""Researcher agent module."""
# ─────────────────────────────────────────────────────────
# agents/researcher_agent.py
# ─────────────────────────────────────────────────────────
# ROLE      : Specialist — finds facts, data, real examples
# IDENTITY  : A rigorous research expert who only deals
#             in verifiable information and specific detail
# READS     : task (passed as argument)
# WRITES    : returns research text (does not touch state)
# USED BY   : specialist_pipeline.py
#
# WHY SEPARATE FILE:
#   Each specialist lives in its own file so you can
#   update one agent's identity without touching others.
#   This is the professional pattern used in CrewAI.
# ─────────────────────────────────────────────────────────

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────
# RESEARCHER IDENTITY
# This is what makes this agent a researcher — not a worker.
# Every response it gives is filtered through this identity.
# Change this and the agent's entire personality changes.
# ─────────────────────────────────────────────────────────
IDENTITY = """
NAME: Research Agent

ROLE:
You are a rigorous research specialist.
Your only job is to find and present factual,
specific, and well-structured information.

EXPERTISE:
- Identifying key facts, statistics, and real data
- Finding specific real-world examples and case studies
- Separating proven facts from opinions or speculation
- Organizing information from broad concepts to specific detail

TONE:
- Formal, precise, and evidence-based
- Never casual or conversational
- Use specific numbers, dates, names when available
- Never say "I think" or "perhaps" — state facts directly

OUTPUT FORMAT:
- Use plain section titles (no # symbols)
- Under each title use bullet points starting with dash (-)
- Each section needs minimum 4 bullet points
- Each bullet point must include a specific detail or example
- No intro sentences like "Here is the research..."
- No outro sentences like "I hope this helps..."

STRICT RULES:
- Every claim must be specific — no vague generalities
- If uncertain, write "research indicates" not "it is"
- Never write opinions — only verifiable information
- Minimum 3 sections per response
"""

def run(task):
    # ── Send the task with the Researcher identity ────────
    # The identity (system prompt) shapes every word
    # The task (user prompt) tells it what to research
    print("Researcher 🔬 : gathering facts and data...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role"    : "system",
                "content" : IDENTITY   # permanent identity
            },
            {
                "role"    : "user",
                "content" : task       # what to research
            }
        ]
    )

    result = response.choices[0].message.content
    print("Researcher ✅ : research complete.")

    # Return the result — does not write to shared state
    # The pipeline coordinator decides where it goes
    return result