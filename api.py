import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from triage import triage
from rules import apply_rules, FinalDecision

logger = logging.getLogger("ticketbot")
app = FastAPI(title="TicketBot")


class TicketIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=5000)


@app.post("/triage", response_model=FinalDecision)
def triage_ticket(ticket: TicketIn):
    try:
        result = triage(ticket.text)
    except Exception:
        logger.exception("triage failed")
        raise HTTPException(status_code=503, detail="Triage failed, try again later")
    return apply_rules(ticket.text, result)


@app.get("/health")
def health():
    return {"status": "ok"}