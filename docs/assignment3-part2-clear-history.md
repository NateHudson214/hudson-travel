# Assignment 3 Part 2 — Confirmed clear saved skills history

Implemented and verified October 26, 2026 (America/New_York). This step uses
fictional messages and mocked replies only. Deletion tests, including browser
confirmation, used disposable temporary databases. No development history was
cleared. This is an implementation step, not a final Part 2 submission.

## Experience

Both session history and conversation history offer **Clear saved skills
history**. A native modal explains that it removes all saved skills sessions,
checkpoints, conversations, messages and mock-run records in this local app,
including the current view's unsaved exercise changes. It explicitly keeps saved
display choices and Hudson Travel records. Cancel and Escape close the dialog
without deleting or discarding local work. Focus begins on Cancel.

Checking the history version is a read only operation. Clear permanently remains
disabled until that read succeeds. Only the explicit confirmation dispatches the
DELETE. Crisis support and Leave are present inside the modal, including loading
and failure states, because the modal makes underlying controls inert. They
close the confirmation and act locally. Returning from resources never starts
breathing. The independent bundled contacts were rechecked; no crisis service
was contacted.

On confirmation, the current view stops local pacing, disposes its queued
session writes, clears recovery markers, and drops its unsaved exercise state.
On success, history lists/details remount to discard stale responses and reload
saved history, with a success message stating that display choices were kept.
Conversation/history requests never start breathing. Other tabs may continue
locally; their older saves cannot restore deleted records.

Once a deletion is dispatched, Close/Leave does not promise to cancel it. A
network failure may leave the outcome unknown; the UI says so and offers **Retry
same clear request** with the original ID/version. It never binds a retry to a
newer generation. A failed initial version read cannot dispatch deletion and
instead offers Refresh confirmation. There are no automatic retries.

## Persistence and stale-write protection

Schema v4 adds skills_history_state: one persistent row containing epoch and the
latest clear request ID, normalized request and response. The response retains
only version/deleted counts, not messages. Explicit migrations from v1/v2/v3
preserve existing records/preferences and initialize epoch 0. Invalid/newer/
partial schemas are rejected. A missing state row fails closed, not reset to 0.

Every session create, event append and conversation turn carries history_epoch.
The application captures it for that session/conversation and preserves it for
all queued requests and retries. It never fetches a new epoch to retry an old
write. The server validates the epoch **inside the write transaction and before
any insert or idempotency replay**. Generation mismatches return 409 with an
instruction to reload the view and choose new activity. Saving fails safely if
an initial status read is unavailable and the client's default epoch is stale;
local exercise, crisis and exit controls remain usable.

Clear uses BEGIN IMMEDIATE, checks the expected epoch, deletes conversations
(cascading messages/runs) and sessions (cascading events), increments epoch, and
records the clear receipt in one transaction. A failed delete rolls everything
back, including the epoch. The synchronous local mock holds its transaction
until completion: either it commits before clear and is deleted, or its old
request arrives after clear and is rejected. No delayed mock can insert after a
successful clear. Future network/provider work must add the separately designed
durable pending/cancelled lifecycle rather than perform network I/O in this lock.

An exact retry of the latest successful clear returns its original receipt
without deleting again. New history written under the new epoch survives that
retry. A changed request under the same ID or a stale distinct clear gets 409.
If another clear has since completed, the older clear retry is stale as well.
Display preference revisions and their save/reset requests are independent.

## API

| Method and path | Contract |
| --- | --- |
| GET /api/skills/history | Returns history_epoch; no mutation or message preview. |
| DELETE /api/skills/history | Strict JSON body: request_id UUID, expected_epoch nonnegative integer, confirm true (strict bool). Returns history_epoch, deleted counts, replayed. |
| POST /api/skills/sessions | Adds history_epoch to existing body. |
| POST /api/skills/sessions/{id}/events | Adds history_epoch to existing body. |
| POST /api/skills/conversations/turns | Adds history_epoch to existing body. |

False/missing/non-boolean confirmation and extra fields such as
 delete_preferences are rejected with 422. Unknown versions/stale operations
return 409; storage failures return sanitized 503. Legacy bodies default to epoch
0 for migration compatibility and are accepted only before the first clear.
Normalization supports existing pre-generation retry records at epoch 0; after
clear those requests are rejected. Session detail includes the matching epoch
for explicit interruption reconciliation. New clients must GET the current epoch
and bind it to a new session/conversation. Skills fetches use cache:no-store.

This is a concurrency boundary in an unauthenticated local coursework app, not
an authorization mechanism. Another browser connected to the same backend shares
this history. Previously displayed content in other tabs may remain until they
refresh/reload. Deleted application rows are not a claim of secure erasure from
SQLite free pages, external copies, backups or prior exported evidence.

## Automated verification

Passed: **465 backend tests**, **81 frontend tests**, both non-fixing frontend
linters, production build (53 modules), diff whitespace and local-link checks.
Two existing dependency deprecation warnings remain. No dependency was installed
or upgraded.

Seventeen new backend cases use temporary databases. They cover all five cleared
tables; preserved preferences/travel; never-dispatched old creates; event and
conversation retries; current generation accepting new records; committed-clear
retries preserving new records; strict confirmation; atomic rollback; concurrent
clear deduplication; a controlled in-progress mock; already-open connections;
schema v3 migration; lost state failing closed; and pre-generation retry migration.
Existing v1/v2 migration tests also pass with schema v4.

Seven added frontend cases cover read/DELETE routing, cache behavior, explicit
confirmation only, unknown-outcome request identity, disposal/late responses,
discarded journal queues, and pinned session/conversation generations. The
existing timing, constrained-reply, preference and travel suites still pass.

Repository root:

```bash
PYDANTIC_DISABLE_PLUGINS=__all__ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests -q
```

frontend/:

```bash
npm test
./node_modules/.bin/oxlint .
./node_modules/.bin/eslint . --no-cache
npm run build
```

## Browser observations and evidence

Used normal Vite and Uvicorn with a temporary QA module importing the actual
FastAPI app, pointing **both databases exclusively under
/private/tmp/skills-clear-qa/**. The module seeded fictional fixtures once and
disabled live providers. It did not use an ASGI bridge or the development DBs.
A temporary fixture backup supported test review; no SQLite files are committed.

1. Opened confirmation, observed Cancel focus, cancelled, and confirmed the seed
   session remained. Crisis support and Leave worked from confirmation without
   clearing records. One browser selector initially matched both banner and modal
   crisis buttons; scoped it to the active dialog. One attempted click followed
   a page reload and found no dialog; inspected state and reopened confirmation.
   These were automation issues, not deletion failures or model failures.
2. Started/paused a fictional session and opened history. Confirmation then cleared
   two sessions, two events, one conversation, two messages and one mock run.
   All five history tables were empty; epoch advanced 0→1. The paused view's
   queue/marker was discarded and history displayed No sessions are saved.
3. Saved display setup stayed simpler/static at preference revision 1. Old session
   and never-dispatched conversation writes at epoch 0 were rejected. Both
   development DB file hashes and the QA travel hash stayed unchanged.
4. Explicitly started a new mock conversation at epoch 1. Only that new fictional
   conversation appeared after reload; the old fixture was absent. New activity
   is permitted, rather than permanently disabling history after a clear.
5. With the QA backend stopped, opening confirmation showed unavailable storage,
   disabled Clear permanently, and retained Cancel, Crisis support and Leave.
   Resources and Leave still worked locally; no second delete was dispatched.
6. Restarted the same QA backend and reloaded. Epoch 1 persisted, cleared sessions
   stayed absent, and only the new conversation remained. The original seed IDs
   were absent. Saved display choices remained available without auto-application.
7. Travel matched Harbor Lantern Hotel T001/T009; Not a Real Hotel removed stale
   offered stays and disabled their selection. No booking/provider action used.
   Final browser warning/error log was empty after reload; expected proxy failures
   occurred during the deliberately stopped-backend case.

- [Confirmation](../evidence/assignment3-part2-clear-history/confirmation.jpg)
- [Clear success](../evidence/assignment3-part2-clear-history/cleared.jpg)
- [Sessions still absent after restart](../evidence/assignment3-part2-clear-history/restart-empty.jpg)
- [Unavailable storage disables deletion](../evidence/assignment3-part2-clear-history/unavailable.jpg)
- [Curated counts/isolation checks](../evidence/assignment3-part2-clear-history/records.json)

Only disposable QA records were deleted. The JSON distinguishes the empty state
immediately after clear from the later, explicitly created new conversation.
Development databases were checked by hashes without exporting their contents.
Test services/tabs were cleaned up; pre-existing user tabs were preserved.

## Limits and next step

No live-model integration/quality evaluation, full accessibility audit, OS motion
preference test, new complete timing measurement, peer evaluation, clean-checkout
run or submission is claimed. There was no commit, push, merge, upload or Canvas
submission. The app's local mock remains the only conversational mode implemented.

Next: review Part 2 readiness against the full assignment and approved design,
identify remaining requirements (including any live-model requirement), finish
necessary mock-based integration evidence, and draft the separate Part 2 report.
Do not turn this implementation step into an unsupported final-completion claim.
