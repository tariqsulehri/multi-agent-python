# ─────────────────────────────────────────────────────────
# message_bus.py
# ─────────────────────────────────────────────────────────
# ROLE    : The shared messaging system between agents
# USED BY : All specialist agents
# CONCEPT : Like a group chat log — every message ever
#           sent is stored here in order.
#           Agents filter messages addressed to them.
#
# WHY NOT USE shared_state.py:
#   shared_state holds the pipeline's current STATUS.
#   message_bus holds agent CONVERSATIONS.
#   Keeping them separate means each does one job clearly.
#   Status and conversation are different concerns.
#
# MESSAGE STRUCTURE:
#   {
#     "from"    : sender agent name (string)
#     "to"      : receiver agent name (string)
#     "type"    : message category (string)
#     "content" : the actual message (string)
#   }
#
# MESSAGE TYPES we use:
#   "finding"  → Researcher shares a discovery
#   "warning"  → Researcher flags a weak area
#   "draft"    → Writer notifies Critic what changed
#   "feedback" → Critic sends rejection reason to Writer
#   "approved" → Critic confirms approval to all
# ─────────────────────────────────────────────────────────

# The bus is just a list — simple and transparent
# Every message ever sent lives here in order
bus = []

def send(from_agent, to_agent, message_type, content):
    # ── Add a new message to the bus ─────────────────────
    # Any agent calls this to send a message to another
    # The message is appended to the end of the list

    message = {
        "from"    : from_agent,    # who is sending
        "to"      : to_agent,      # who should receive
        "type"    : message_type,  # category of message
        "content" : content        # the actual text
    }

    bus.append(message)

    # Print every message in terminal so you can follow
    # the agent conversation as it happens live
    print(
        f"\n📨 [{from_agent} → {to_agent}] "
        f"({message_type}): {content[:80]}..."
        if len(content) > 80
        else
        f"\n📨 [{from_agent} → {to_agent}] "
        f"({message_type}): {content}"
    )

def read(to_agent, message_type=None):
    # ── Read all messages addressed to a specific agent ──
    # to_agent     = only return messages sent to this agent
    # message_type = optional — filter by type too
    #
    # Example: read("Writer", "warning")
    # Returns all warning messages sent to the Writer

    if message_type:
        # Filter by both receiver AND type
        return [
            msg for msg in bus
            if msg["to"] == to_agent
            and msg["type"] == message_type
        ]
    else:
        # Filter by receiver only — return all types
        return [
            msg for msg in bus
            if msg["to"] == to_agent
        ]

def read_all():
    # ── Return entire message history ─────────────────────
    # Used by the pipeline to save full conversation log
    # Also useful for debugging — see every message sent
    return bus

def clear():
    # ── Clear all messages ────────────────────────────────
    # Called at the start of each pipeline run
    # Without this old messages from last run stay in bus
    bus.clear()

def summary():
    # ── Print a readable summary of all messages ─────────
    # Called at the end of the pipeline for a full log
    print("\n── Message Bus Summary ──")
    if not bus:
        print("   No messages sent.")
        return
    for i, msg in enumerate(bus):
        print(
            f"   {i + 1}. [{msg['from']} → {msg['to']}] "
            f"({msg['type']}): {msg['content'][:60]}..."
            if len(msg['content']) > 60
            else
            f"   {i + 1}. [{msg['from']} → {msg['to']}] "
            f"({msg['type']}): {msg['content']}"
        )