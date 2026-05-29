# ─────────────────────────────────────────────────────────
# shared_state.py
# ROLE    : The whiteboard every agent reads and writes to
# USED BY : All agents
# NEW     : Added retry_count, feedback, complexity fields
#
# FLOW:
#   idle → planning → working → collecting → review
#        → approved (done) OR rejected (back to working)
# ─────────────────────────────────────────────────────────

state = {
    # ── Main task ──────────────────────────────────────────
    "main_task"   : None,      # The big task typed by the user

    "status"      : "idle",    # Overall pipeline stage:
                               #   idle       → nothing started
                               #   planning   → Manager thinking
                               #   working    → Workers running
                               #   collecting → Collector combining
                               #   reviewing  → Reviewer checking
                               #   approved   → Reviewer said yes
                               #   rejected   → Reviewer said no
                               #   error      → something broke

    # ── Complexity (set by Manager) ────────────────────────
    "complexity"  : None,      # How complex is the task?
                               #   "simple"  → 1 worker
                               #   "medium"  → 2 workers
                               #   "complex" → 3 workers

    # ── Sub-tasks (created by Manager) ────────────────────
    "sub_tasks"   : [],        # List of sub-tasks for Workers
                               # Length = 1, 2, or 3
                               # based on complexity

    # ── Results (filled by Workers) ───────────────────────
    "results"     : {},        # Dict of Worker results
                               # Key   = worker index (0,1,2)
                               # Value = text from OpenAI

    # ── Combined result (created by Collector) ────────────
    "combined_result" : None,  # All results joined into one
                               # This is what Reviewer checks

    # ── Feedback loop (NEW) ────────────────────────────────
    "retry_count" : 0,         # How many times Worker has retried
                               # Max = 3 before pipeline gives up

    "feedback"    : None,      # Message from Reviewer to Worker
                               # Example: "Add more detail to
                               # section 2 and fix the structure"
                               # Worker reads this on retry

    # ── Quality flags ─────────────────────────────────────
    "formatted"   : False,     # True after Formatter cleans result
    "approved"    : False,     # True after Reviewer says yes

    # ── Error tracking ────────────────────────────────────
    "error"       : None       # Error message if anything fails
}