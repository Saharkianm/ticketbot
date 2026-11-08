import json
from schema import Category, Priority

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

for t in tickets:
    # These raise an error if a label isn't in our allowed lists
    Category(t["expected_category"])
    Priority(t["expected_priority"])

print(f"OK: {len(tickets)} tickets, all labels valid")