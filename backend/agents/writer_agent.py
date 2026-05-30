# ─────────────────────────────────────────────────────────
# agents/writer_agent.py
# ─────────────────────────────────────────────────────────
# ROLE      : Specialist — takes raw research and turns
#             it into clear, readable, well-structured prose
# IDENTITY  : A professional writer who values clarity
#             and reader experience above all else
# READS     : task + research (both passed as arguments)
# WRITES    : returns written draft (does not touch state)
# USED BY   : specialist_pipeline.py
#
# WHY THIS MATTERS:
#   The Researcher finds facts but writes like a database.
#   The Writer takes those facts and makes them readable.
#   Separation of concerns — each agent does one thing well.
# ─────────────────────────────────────────────────────────

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# ─────────────────────────────────────────────────────────
# WRITER IDENTITY
# Notice the difference in tone from the Researcher.
# The Researcher is cold and factual.
# The Writer is warm, clear, and reader-focused.
# Same facts — completely different voice.
# ─────────────────────────────────────────────────────────
IDENTITY = """
NAME: Writer Agent

ROLE:
You are a professional content writer.
Your job is to take research material and turn it
into clear, well-structured, readable content.

EXPERTISE:
- Transforming dense research into readable prose
- Structuring content logically for the reader
- Making complex topics accessible without losing accuracy
- Writing with clarity, flow, and appropriate depth

TONE:
- Clear and confident — not academic, not casual
- Active voice wherever possible
- Short sentences for complex ideas
- Vary sentence length to maintain rhythm

OUTPUT FORMAT:
- Use plain section titles (no # symbols, no markdown bold)
- Under each title use bullet points starting with dash (-)
- Each bullet point is one complete, clear thought
- Minimum 3 bullet points per section
- No intro sentences like "In this piece..."
- No outro sentences like "In conclusion..."

STRICT RULES:
- Never invent facts not present in the research provided
- Keep all specific data, numbers, and examples from research
- If research is thin on a point, expand the explanation —
  do not invent new facts
- Every section must connect logically to the next
- Write for a reader who is intelligent but not an expert
"""

def run(task, research):
    # ── Send task + research to the Writer ───────────────
    # The Writer receives BOTH:
    #   task     = what the final output should cover
    #   research = the raw facts from the Researcher
    # It must use the research — not invent new facts
    print("Writer ✍️  : drafting content from research...")

    # We combine task and research into one message
    # This tells the Writer exactly what it has to work with
    message = (
        f"Task: {task}\n\n"
        f"Research to use:\n{research}\n\n"
        f"Write structured content based on this research."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role"    : "system",
                "content" : IDENTITY   # permanent writer identity
            },
            {
                "role"    : "user",
                "content" : message    # task + research material
            }
        ]
    )

    result = response.choices[0].message.content
    print("Writer ✅ : draft complete.")

    return result