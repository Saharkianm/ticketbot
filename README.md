# TicketBot



Support ticket triage service. It reads a customer message and returns a

category, a priority, and a recommended action (auto reply, route to a team,

or escalate to a human), together with a record of which rules changed the

outcome.



Runs fully locally: phi3 through Ollama, FastAPI for the API.



## How it works



1\. **Model (phi3).** Reads the ticket and fills a fixed schema: reasoning,

&#x20;  category, priority, a yes/no security flag, and an action.

2\. **Policy (`policy\_action` in `rules.py`).** The final action is decided in

&#x20;  code from the priority, not taken from the model:

&#x20;  - urgent goes to a human

&#x20;  - low priority, non-technical tickets get an auto reply

&#x20;  - everything else goes to a team

3\. **Rules (`rules.py`).** Safety checks that run after the policy:

&#x20;  - legal language (lawyer, lawsuit, chargeback...) forces escalation

&#x20;  - the model's security flag (someone else used the account) forces escalation

&#x20;  - security or technical keywords only mark the ticket `needs\_review`

&#x20;  - a high priority ticket never gets an auto reply



Why the layers: the model is good at reading a ticket and unreliable at

decisions, so anything costly is decided by plain code. Every response includes

`rules\_fired`, which lists which rules changed the outcome, and `needs\_review`,

which marks tickets a person should double-check.



## Setup and run



On Windows (CMD):



```

python -m venv venv

venv\\Scripts\\activate

pip install pydantic ollama fastapi uvicorn

ollama pull phi3

uvicorn api:app --reload

```



Open http://127.0.0.1:8000/docs, choose `POST /triage`, and send:



```

{"text": "I was charged twice this month"}

```



Empty or whitespace-only text is rejected with a 422 error before the model is

called. If the model fails, the API returns a 503 and logs the real error.



## Files



\- `schema.py` - allowed categories, priorities, actions, and the output shape

\- `triage.py` - the prompt and the call to the model

\- `rules.py` - the policy and the safety rules

\- `api.py` - the FastAPI service

\- `tickets.json` - 33 sample tickets with expected labels

\- `evaluate.py` - scores all tickets and prints the mistakes

\- `why.py` - shows which layer made a decision (`python why.py 17 22`)

\- `reasons.py` - checks the reasoning text for empty or label-only notes

\- `check\_step1.py` - validates the labels in `tickets.json`

\- `compare.py`, `run\_step2.py`, `run\_step3.py` - earlier experiments, kept for

&#x20; history



## Results on the 33 sample tickets



\- Category correct: 31/33

\- Priority correct: 25/33

\- Tickets that needed a human and got one: 10/10

\- Tickets that did not need one but were escalated: 1/23 (the model's own

&#x20; action alone would have escalated 3/23)



In the last run the model's own action also reached 10/10 on tickets that

needed a human, so these numbers do not show that the rules added safety in

general. See below.



These numbers are optimistic. See the limitations.



## Model choice



phi3 was compared with gemma:2b on the first 8 tickets with an earlier version

of the prompt: phi3 got 7/8 categories and 7/8 priorities, gemma:2b got 5/8

and 3/8, and gemma almost never escalated. This is a small test, so treat it

as a rough ranking only.



## Known limitations



\- **Small, self-made test set.** The 33 tickets were written by one person,

&#x20; and the prompt and rules were adjusted after reading their errors. The

&#x20; scores are not an accuracy estimate for real customer messages. The first

&#x20; thing to do before real use is test on real tickets.

\- **Priority is the weakest field.** It tends to be one level too severe. The

&#x20; security flag is what escalates compromised-account tickets when the

&#x20; priority comes out too low (seen on tickets 17 and 22, both written by the

&#x20; author, so treat as a small sample).

\- **Keyword rules are English-only,** and phi3's handling of other languages

&#x20; has not been tested.

\- **False alarms exist.** Any ticket containing words like "legal" is

&#x20; escalated, even in a harmless request (ticket 11).

\- **Ticket 7 (data loss plus a legal threat) is sometimes given the wrong

&#x20; category.** It is still escalated by the legal rule.

\- **The `reasoning` text is a model note, not evidence.** The last automatic

&#x20; check found no empty or one-word notes, but a note can still be wrong

&#x20; (ticket 24 invents a workaround), can contradict the labels, and often

&#x20; contains garbled words. Use `rules\_fired` as the audit trail and never show

&#x20; `reasoning` to customers.

\- **The policy table is a guess.** Which tickets go to a human, a team, or an

&#x20; auto reply is a business decision and should be set by the support team. For

&#x20; example, a double charge is currently routed to a team, not a human.

\- **Prompt changes have side effects.** Editing the prompt or schema moved

&#x20; unrelated tickets every time. Re-run `evaluate.py` after any change.

\- **Local model speed.** Each ticket takes seconds, and the first request after

&#x20; startup is slower while the model loads.



## Next steps



\- Test on 30 to 50 real, anonymized tickets.

\- Have the support team review and set the policy table.

\- Decide whether a double charge should reach a human.

