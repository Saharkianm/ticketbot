import json
from triage import triage

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

bad = 0
for t in tickets:
    r = triage(t["text"], model="phi3")
    ok = len(r.reasoning) >= 30 and not r.reasoning.lower().startswith("security")
    bad += not ok
    print(t["id"], "OK " if ok else "BAD", r.reasoning)

print(f"\n{bad}/{len(tickets)} look bad")