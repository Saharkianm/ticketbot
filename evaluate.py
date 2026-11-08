import json
from triage import triage
from rules import apply_rules

MODEL = "phi3"

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

cat_ok = pri_ok = 0
need_total = need_before = need_after = 0
no_need_total = false_before = false_after = 0

for t in tickets:
    result = triage(t["text"], model=MODEL)
    decision = apply_rules(t["text"], result)

    cat_ok += result.category.value == t["expected_category"]
    pri_ok += result.priority.value == t["expected_priority"]

    if result.category.value != t["expected_category"] or result.priority.value != t["expected_priority"]:
        print(f"Label miss: ticket {t['id']}: expected {t['expected_category']}/{t['expected_priority']}, "
              f"got {result.category.value}/{result.priority.value}")

    # Does this ticket need a human? Default: urgent tickets do.
    should = t.get("should_escalate", t["expected_priority"] == "urgent")
    before = result.action.value == "escalate_to_human"
    after = decision.final_action.value == "escalate_to_human"

    if should:
        need_total += 1
        need_before += before
        need_after += after
        if not after:
            print(f"MISSED escalation: ticket {t['id']}")
    else:
        no_need_total += 1
        false_before += before
        false_after += after
        if after:
            print(f"Over-escalated: ticket {t['id']} (rules: {decision.rules_fired})")

n = len(tickets)
print(f"\nCategory accuracy: {cat_ok}/{n}")
print(f"Priority accuracy: {pri_ok}/{n}")
print(f"Needed a human:    model alone {need_before}/{need_total}  ->  with rules {need_after}/{need_total}")
print(f"Didn't need one:   model alone {false_before}/{no_need_total} escalated  ->  with rules {false_after}/{no_need_total}")