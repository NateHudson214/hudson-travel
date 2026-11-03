# Part 3 repeated live checks — November 2, 2026

Four authorized real OpenAI dispatches using `gpt-6-luna`: three completed
expected selections and one timeout. No automatic retries or fifth call.
Mock mode is restored. This is a small fictional selection/availability sample,
not a clinical result or a reliable success-rate estimate.

## Pricing, allowance and method

Before sending, the official [pricing](https://developers.openai.com/api/docs/pricing)
and [model page](https://developers.openai.com/api/docs/models/gpt-6-luna) were
opened. Standard rates remain $0.10 input/$0.50 output per million tokens;
cached input $0.01, cache writes $0.125 (30-minute)/$0.25 (12-hour).
The bounded request (20,000 serialized bytes, 512 output tokens) remains well
within the conservative $0.10 reservation per attempt at these prices.

The original durable database began at 4/10 calls and $0.40/$1 reserved, with no
pending runs. It now has **8/10 calls and $0.80 reserved; two calls/$0.20 remain**.
The timed-out dispatch counts and is not refunded. These are reservations, not
an invoice. Received successful responses reported 1,621 input and 157 output
tokens, giving $0.0002406 at uncached standard rates for those three alone.
The timeout's usage/charge is unknown; no total billed-cost claim is made.

A single-use harness called the actual FastAPI route through ASGITransport;
the production adapter used real HTTPS transport with retries=0. A passive
observer retained only status/model/usage metadata, not raw provider prose,
reasoning or error bodies. No browser Send or live UI verification is claimed.
The child process enabled live only inside a try/finally block, restored mock,
then restored the originally disabled environment. `.env` was unchanged.
An exclusive journal blocks accidental batch rerunning. No availability probe
or hidden provider request was sent. A preflight wrong `.env` path was corrected
before any request or journal; this was not a provider retry. A read-only
verification query also needed the actual session-events table name corrected.

Each pair used the identical fictional input in independent empty conversations,
with the same saved preferences/context hash, instructions and reply catalog.
Typing was before; motion was after with no session association, so no new
completed exercise is implied. Expected reply and required facts were saved
before sending. All route responses were HTTP 200, including the fixed fallback;
that status alone is not model success. No timeout setting or app code changed.

| Case | Expected reply / required fact | Observed | Route elapsed |
| --- | --- | --- | --- |
| Typing 1 | explain_available_skill / no_typing_required | Failed: timeout, fixed application fallback; no model selection observed | 3066 ms |
| Typing 2 | explain_available_skill / no_typing_required | Completed: exact expected reply/fact | 1522 ms |
| Motion 1 | neutral_acknowledgment / static_display_option | Completed: exact expected reply/fact | 2693 ms |
| Motion 2 | neutral_acknowledgment / static_display_option | Completed: exact expected reply/fact | 1838 ms |

The three received responses reported `gpt-6-luna`; no dated model snapshot was
supplied. The timeout has only the configured identifier, not a returned model.
Both motion replies selected the same reply/fact and rendered identical approved
text despite different latency/token counts. Typing yielded one unavailable
result and one valid selection; it does not provide two successful selections
for measuring typing selection consistency. The earlier Part 2 one-off is not
silently substituted. Four attempts exhaust this batch authorization.

## Failure, decision and verification

The real timeout reached the adapter's finite three-second deadline and saved
an `application-fallback` with failed/live/timeout metadata. It did not save
unreviewed output or automatically redispatch. This exposes an availability cost
of the strict deadline that the earlier one-off sample did not encounter.
Keep the finite deadline and optional continue-without-conversation behavior;
do not increase it or spend more solely to improve the observed result.

Independent SQLite verification found four new conversations/eight messages and
four final runs (one failed, three completed), no pending run, valid integrity and
foreign keys. All existing sessions/events/conversations/messages/runs/control
rows remain unchanged. Preferences/history epoch, travel DB, `.env`, Part 1/2
reports and evaluated application source are unchanged. The original ledger was
advanced, never replaced/reset. All four history detail reads returned 200 after
mock restoration without another provider call. No server was started.

Relevant mocked regression checks: **164 skills backend tests passed**, two
existing dependency deprecation warnings. The preceding full mock gate remains
492 backend/87 frontend plus lint/build; it was not rerun or relabeled here.
No dependency, source change, installation, commit, push or submission occurred.

Evidence: [batch, predeclared expectations, route results and usage](../evidence/assignment3-part3-live-checks/batch.json),
[independent verification](../evidence/assignment3-part3-live-checks/verification.json).
Next: clean-checkout verification, final recordings/code explanation, final
report/readiness review, then separately authorized publication/submission steps.
Further live calls require fresh explicit authorization and share the two-call
remaining allowance; none is needed just to finish documentation or read history.
