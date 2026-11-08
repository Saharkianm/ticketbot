from enum import Enum
from pydantic import BaseModel


class Category(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    feature_request = "feature_request"
    other = "other"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Action(str, Enum):
    auto_reply = "auto_reply"
    route_to_team = "route_to_team"
    escalate_to_human = "escalate_to_human"


class TriageResult(BaseModel):
    reasoning: str
    category: Category
    priority: Priority
    security_concern: bool
    action: Action