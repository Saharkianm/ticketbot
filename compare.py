import json
from triage import triage

MODELS = ["phi3", "gemma:2b"]  # use the exact names shown by `ollama list`

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

for model in MODELS:
    cat_ok = pri_ok = 0
    print(f"\n===== {model} =====")
    for t in tickets:
        r = triage(t["text"], model=model)
        c = r.category.value == t["expected_category"]
        p = r.priority.value == t["expected_priority"]
        cat_ok += c
        pri_ok += p
        if not (c and p):
            print(f"Ticket {t['id']}: expected {t['expected_category']}/{t['expected_priority']}, "
                  f"got {r.category.value}/{r.priority.value}/{r.action.value}")
    print(f"category {cat_ok}/{len(tickets)}, priority {pri_ok}/{len(tickets)}")