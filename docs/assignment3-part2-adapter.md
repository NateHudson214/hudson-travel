# Disabled skills model adapter — October 26, 2026

**Later authorized check:** four real OpenAI calls subsequently passed their
recorded expectations, and mock mode was restored. Six calls/$0.60 reservation
allowance remain. See [live results and limits](assignment3-part2-live-checks.md).
The original implementation/verification snapshot below predates that batch;
its statements that no real call had occurred describe that earlier step.

Implemented with simulated provider responses only. **Live mode remains disabled.**
Student choices: OpenAI, configured model `gpt-6-luna`, at most ten dispatches and
$1 total for skills testing. Existing `OPEN_AI` is reused only on the backend;
the travel `OPENAI_MODEL` setting does not change the skills model. No dependency
was installed, no credential was changed, and no paid call was made.

## Configuration and response contract

`SKILLS_MODEL_MODE=mock` is the default when absent or set to any value other than
`live`. `.env.example` documents mock mode; the actual `.env` was not edited.
There is no browser control or HTTP endpoint that enables live mode. A future
host change to `live` requires separate student authorization. The composer first
loads `/api/skills/model-status`, shows provider disclosure if live, then includes
`allow_live: true` only for that disclosed composer. Old mock composers cannot
silently begin sending to a newly enabled provider. An explicit client opt-in
alone cannot override the host setting. Missing credentials produce a safe error
without dispatch or charge. Standard startup commands are unchanged.

The versioned instruction file is
`backend/app/skills/prompts/selector-v1.md`. The application supplies the approved
reply/fact catalog, before/after placement, associated terminal-session facts,
only this conversation's six latest messages (at most 3000 characters), the new
fictional message (at most 500 characters), and explicitly saved display choices
if present. IDs, other conversations and unsaved display choices are excluded.
The context hash includes the instruction-file hash; `context_version` records
`skills-selector-v1/skills-replies-v1`. Configured model IDs are provenance,
not proof of actual account access or provider-resolved model snapshots.

The adapter sends one Responses API request with `store: false`, standard tier,
no tools, a strict JSON schema and at most 512 output tokens. Total serialized
request size is capped at 20,000 UTF-8 bytes. It accepts exactly one completed
assistant output-text object with reviewed `reply_id` and at most two compatible
`fact_ids`. Duplicate JSON keys, free prose, unknown/extra fields, refusals,
incomplete/multiple outputs, incompatible facts and oversized responses fail.
The application renders catalog text only. Raw rejected output, credentials and
provider error bodies are not stored or displayed. The adapter has a three-second
total asynchronous deadline, finite transport timeouts, no redirects, no proxy
inheritance and no automatic retries. Parsing/storage overhead is additional;
the client retains its existing five-second request timeout and exact-ID retry.

Official documentation checked October 26, 2026:
[model capabilities](https://developers.openai.com/api/docs/models/gpt-6-luna),
[structured output format](https://developers.openai.com/api/docs/guides/structured-outputs),
and [pricing](https://developers.openai.com/api/docs/pricing). The model page lists
structured outputs and standard text rates of $0.10 input/$0.50 output per million
tokens (cache writes $0.125). Account access and real response behavior remain
unverified. Recheck settings/pricing before any separately authorized live test.

## Storage, cancellation, deletion and durable allowance

Schema version 5 explicitly migrates versions 1–4 in one transaction, preserving
sessions, messages, completed mock runs, preferences and history generation.
The checked run table now permits `pending`, `completed`, `failed`, `cancelled`
and mock/live modes; message provenance distinguishes live-selected templates.

Before provider I/O, a short transaction validates the generation, request ID,
conversation revision and association; writes the user message/pending run/control
record; and reserves the allowance. It then commits. Provider waiting holds no
SQLite transaction/write lock. A second transaction must find the original
pending run and matching generation before saving an assistant message. It never
upserts a missing conversation/run. A duplicate exact request returns its saved
pending/final state; a changed payload conflicts. Only one pending turn per
conversation is allowed. Explicit retry of an ambiguous request uses the same ID
and does not dispatch again, even after restart or allowance exhaustion.

`POST /api/skills/runs/{request_id}/cancel` accepts `history_epoch`. Leaving or
continuing to breathing requests this cancellation without waiting and ignores
late UI results. A cancellation intent that arrives before Send prevents that
request from starting. Cancelling a pending run saves a fixed application fallback
and `cancelled` status; a late provider result cannot replace it. Cancellation
cannot promise to recall an already dispatched request or avoid its cost.
`GET /api/skills/runs/{request_id}?history_epoch=...` reads its saved status.
A pending response can be checked with the same turn ID through explicit Retry;
there is no automatic second provider dispatch or polling loop.

Pending runs have ten-second recovery leases. On the next conversation/history/
status request after process restart or lease expiry, they become failed with
`interrupted`, without redispatch. The supported coursework server is one backend
worker/process, as in the README commands. Recovery is lazy rather than a claim
of background monitoring. The application does not recover an unsent draft after
browser close. A final-save failure leaves the durable pending record available
for status/recovery, never an automatic second model call.

Confirmed history clearing removes conversations/runs/control intents and sessions
in the same transaction, advances the persistent generation, and leaves saved
display choices and the allowance ledger intact. Older queued/retried sends,
cancellations, or late completions conflict instead of recreating cleared data.
The ledger contains only model/configuration/counters, not conversation text or
request IDs. Clearing history is not an allowance reset.

`skills_call_budget` is a single durable ledger in the separate skills database:
10 calls, 1,000,000 microdollars ($1), initially zero reservations. Before each
possible dispatch it atomically reserves one call and 100,000 microdollars
($0.10). Failures, timeouts, cancellation and crashes never refund reservations;
a crash before actual HTTP dispatch can conservatively consume one. With the
bounded text-only request and verified prices, this reservation exceeds the
request's calculated token-cost bound. It is not a measurement of billed cost.
The ledger survives history deletion, reload, server restart and mode toggles.
Parallel requests cannot overspend it. Exhausting either limit switches new turns
to labeled fixed mocks; prior request IDs keep their original result/mode.
There is no reset/refill HTTP endpoint. Preserve this local database for the
approved testing allowance; creating a new database would create a new ledger.
This bounds this adapter, not unrelated travel calls/account-wide spending or
future changed provider pricing. It is not an OpenAI account billing limit.

## Verified checks and remaining work

- Full backend suite: **492 passed**, two existing dependency deprecation warnings.
- Frontend: **85 passed**, non-fixing oxlint/ESLint and production build passed.
- Temporary-database/MockTransport cases cover disabled/disclosure gates, exact
  replay, bounded context and saved choices, rejected output, sanitized HTTP
  failures, timeout, missing configuration, cancellation before/during dispatch,
  late-result rejection, deletion during dispatch, no lock across I/O, recovery,
  final-save failure, migration preservation, independent dollar limit and
  parallel cap exhaustion. None sends a real provider request.
- Browser check with the actual FastAPI app and Vite development/production preview, temporary skills/travel
  databases, disabled live flag and no usable keys: optional before conversation
  displayed the mock disclosure and saved the approved typing/pause reply;
  Crisis support opened directly and Leave returned immediately to idle.
  SQLite v5 integrity and foreign keys passed; reservations stayed zero.
  [Browser evidence](../evidence/assignment3-part2-adapter/mock-conversation.jpg)
  and [curated records](../evidence/assignment3-part2-adapter/browser-records.json).
  [Local source fingerprint](../evidence/assignment3-part2-adapter/source-manifest.json)
  identifies the reviewed uncommitted source, not a submitted Git commit.
- The browser used a temporary harness to isolate data and forbid providers, not
  an altered application entry point. The environment initially blocked opening
  local ports; the same servers started after local-port permission. Only these
  test servers/tabs were closed afterward. The development screen reset between
  later interactions (cause unestablished); final confirmation and the screenshot
  were repeated against the built production preview. This is not claimed as a
  repaired application defect. Development database hashes remained
  unchanged. No new 60-second timing result is claimed; the timer was unchanged.
- Live provider connectivity, account/model access, usefulness of model selection,
  refusals/variation and actual billed usage remain unverified. No live mode was
  enabled outside simulated tests. No checkpoint/publication/submission occurred.

Next authorized step can be at most four fictional live checks (typing, motion,
unsupported request, fictional support reference), sharing the existing ten-call/
$1 allowance. First inspect the durable remaining allowance and current pricing,
make no automatic retries, record actual model/mode/results, restore mock mode,
and rerun affected checks. The student must authorize enabling/calls separately.
The model-contribution submission requirement remains outstanding until verified
live evidence or explicit instructor approval for mocks. Follow the readiness
review for remaining checkpoint/evidence-access/submission steps.
