import json
import sys
from triage import triage
from rules import apply_rules

with open("tickets.json", encoding="utf-8") as f:
    tickets = {t["id"]: t for t in json.load(f)}

ids = [int(x) for x in sys.argv[1:]] or [22, 28, 29, 31, 32, 33]

for tid in ids:
    t = tickets[tid]
    r = triage(t["text"], model="phi3")
    d = apply_rules(t["text"], r)
    print(tid, r.category.value, r.priority.value, "| flag:", r.security_concern,
          "| model action:", r.action.value, "| final:", d.final_action.value, d.rules_fired)