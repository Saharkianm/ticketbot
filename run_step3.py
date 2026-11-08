import json
from triage import triage
from rules import apply_rules

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

for t in tickets:
    result = triage(t["text"], model="phi3")
    decision = apply_rules(t["text"], result)
    changed = decision.final_action != result.action
    if decision.rules_fired:
        print(f"Ticket {t['id']}: model said {result.action.value}, "
              f"final {decision.final_action.value}, "
              f"review={decision.needs_review}")
        print(f"   rules: {decision.rules_fired}")