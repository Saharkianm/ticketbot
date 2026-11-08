import json
from triage import triage

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

for t in tickets:
    result = triage(t["text"])
    print(f"--- Ticket {t['id']}: {t['text'][:60]}...")
    print(f"  expected: {t['expected_category']} / {t['expected_priority']}")
    print(f"  got:      {result.category.value} / {result.priority.value} / {result.action.value}")
    print(f"  reason:   {result.reasoning}")