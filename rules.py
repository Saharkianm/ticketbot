import re
from pydantic import BaseModel
from schema import TriageResult, Action, Priority, Category

LEGAL_PATTERN = re.compile(
    r"\b(lawyer|legal|sue|lawsuit|court|fraud|chargeback)\b", re.IGNORECASE
)
TECH_HINT_PATTERN = re.compile(
    r"\b(crash\w*|data loss|bug|error)\b", re.IGNORECASE
)
# The "." in "didn.t" matches both ' and ’ (phones often type the curly one)
SECURITY_PATTERN = re.compile(
    r"(didn.t do (it|that)|did not do (it|that)|hacked|unauthori[sz]ed|"
    r"someone (else )?(logged|accessed|got into|changed))",
    re.IGNORECASE,
)


class FinalDecision(BaseModel):
    triage: TriageResult
    final_action: Action
    needs_review: bool
    rules_fired: list[str]


def policy_action(result: TriageResult) -> Action:
    # My guess at a policy. The real one is a business decision.
    if result.priority == Priority.urgent:
        return Action.escalate_to_human
    if result.priority == Priority.low and result.category != Category.technical:
        return Action.auto_reply
    return Action.route_to_team


def apply_rules(ticket_text: str, result: TriageResult) -> FinalDecision:
    action = policy_action(result)
    needs_review = False
    fired = []

    # Rule 1: legal language always goes to a human
    if LEGAL_PATTERN.search(ticket_text) and action != Action.escalate_to_human:
        action = Action.escalate_to_human
        fired.append("legal_language -> escalate")

    # Rule 2: security wording is a weak signal: flag for review, don't override
    if SECURITY_PATTERN.search(ticket_text):
        needs_review = True
        fired.append("security_language -> needs_review")

    # Rule 2b: the model flagged a possible account compromise
    if result.security_concern and action != Action.escalate_to_human:
        action = Action.escalate_to_human
        fired.append("model_security_flag -> escalate")

    # Rule 3: never auto-reply to a high-priority ticket
    if result.priority == Priority.high and action == Action.auto_reply:
        action = Action.route_to_team
        fired.append("high_priority_no_autoreply -> route")

    # Rule 4: flag (don't override) when text hints at a technical problem
    # but the model chose another category
    if TECH_HINT_PATTERN.search(ticket_text) and result.category != Category.technical:
        needs_review = True
        fired.append("category_mismatch_hint -> needs_review")

    return FinalDecision(
        triage=result,
        final_action=action,
        needs_review=needs_review,
        rules_fired=fired,
    )