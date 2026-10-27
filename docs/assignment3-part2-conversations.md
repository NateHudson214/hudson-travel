# Assignment 3 Part 2 — Optional mocked conversation

Implemented October 26, 2026. This step is local coursework functionality using
fictional messages. It does not establish live-model integration, interpretation
quality, clinical effectiveness, or completion of Part 2.

## User flow and ownership

From the ready exercise view, choose **Optional mock conversation before
breathing** or start breathing directly. After completion or stopping, conversation
is optional again. Conversation is never presented inside a running/paused
exercise. Continue returns to exercise options without starting it. Crisis
support and Leave stay available while loading or failing, including simpler
view. No response can change the timer, navigation, motion choice, or preferences.

The composer identifies fixed mocks and unencrypted local storage before Send.
Blank/over-500-character input is rejected. No personal disclosures should be
entered. A failed network/storage request preserves the draft and exact request
for explicit **Retry same turn**. No automatic retry or live-provider fallback
exists. Leaving unmounts the composer; late responses cannot reopen it or alter
the exercise. A dispatched turn may still finish saving after leaving, as the UI
explains. Unsent drafts and retry IDs do not survive closing/reloading the page.

Conversation history is separate from session history. Summaries show placement,
date, and mock labeling, without previews. Opening a summary reads saved messages;
GET requests never produce replies. Messages are rendered as escaped Vue text.
History is read-only in this step; return to exercise options for a new
conversation. No automatic latest-message disclosure or cross-conversation search.

## API contract

- `POST /api/skills/conversations/turns` accepts exactly conversation_id and
  request_id (UUIDs), expected_revision (strict nonnegative integer), placement
  (before/after), session_id (nullable UUID), and message (1–500 characters,
  trimmed before saving). Unknown fields, including mode/model/output, fail 422.
- The first turn uses expected_revision 0. Each saved user/assistant pair advances
  revision by two. Stale revisions or changed placement/association fail 409.
- Every new turn has a new request_id. Exact retries return the original pair/run
  with replayed true, even after later turns. Reusing the ID with different
  normalized data fails 409. Creation, both messages, revision, and run commit
  atomically, or all roll back. No pending half-pair is visible.
- `GET /api/skills/conversations?limit=20&cursor=...` returns conversations and
  next_cursor, newest first with conversation_id breaking timestamp ties. Limit
  is 1–50. Invalid cursor is 400.
- `GET /api/skills/conversations/{id}?limit=50&after_sequence=0` returns
  conversation, ordered messages, and next_after_sequence; missing record is 404.
  Storage failures are sanitized 503 responses. No raw database/provider errors.

Before-conversation has no session association because exercise creation remains
optional. After-conversation links to the finished/stopped/interrupted session
only when its latest checkpoint is acknowledged. If saving is unavailable or
pending it remains an independent after-conversation; breathing/exit is not
blocked. The server rejects associations to an unfinished session or a before
placement. It never changes session progress. Retrospective attachment of a
before-conversation is deferred.

## Schema version 2 and preserved data

The same separate skills database now adds three tables to its existing three:

| Table | Records |
| --- | --- |
| skills_conversations | UUID, optional session FK (SET NULL), before/after placement, UTC timestamps, revision. |
| skills_messages | UUID, conversation FK (CASCADE), unique ordered sequence, user/assistant role, bounded visible content, source, timestamp, approved reply ID and fact IDs. |
| skills_model_runs | Unique request ID, conversation/user-message FKs, normalized retry body and original response, completed/failed status, mock mode, fixture ID, context version/hash, sanitized failure category, timestamp. |

An explicit transactional v1→v2 migration checks legacy table/metadata versions,
adds conversation tables/index, then updates PRAGMA user_version and metadata.
Existing sessions/events are preserved. New databases initialize at v2; foreign,
partial, corrupt, or newer databases fail closed. Each request owns its SQLite
connection. check_same_thread=False supports FastAPI entering, using, and closing
a sync dependency on different worker threads; transactions still serialize
writes and connections are never shared between requests.

Local data is plaintext and unauthenticated. There is no new dependency,
environment variable, provider credential, installation step, or background job.
Deleting/resetting history is deferred. The subsequent display-choice step adds
optional saved display preferences and reset; see the
[preferences guide](assignment3-part2-preferences.md).

## Approved response and context boundary

`backend/app/skills/conversations.py` imports the existing reviewed catalog and
renderer in replies.py. Default `fixed_mock` returns before=explain_available_skill
with no_typing_required and pause_or_stop; after=neutral_acknowledgment with
static_display_option. It is a deterministic fixture, not text interpretation or
a distress detector. The browser explains that limitation. No provider client,
configuration, live mode switch, tool execution, generated SQL, or model-written
therapeutic prose is available in these routes.

The fixture receives only the approved catalog/version, placement, associated
skill/version/status facts if present, this conversation's last six messages
(trimmed oldest-pair-first to 3000 characters), and the new fictional message.
No other conversations, travel data, user/session IDs, hidden reasoning, inferred
feelings, or global preferences are included. Context is hashed (context_hash)
for reproducibility rather than claiming a real provider prompt/model was used.

The unchanged render_reply validates exactly reply_id/fact_ids, compatibility,
deduplication, at most two facts, and ≤600 rendered characters. Malformed replies
and selector exceptions save a failed mock run plus the fixed application
fallback, with no raw rejected output or exception. Successful source is
mock-selected-template; fallback source is application-fallback. Fixture ID is
local-fixed-fixture-v1 and mode is mock, never a fabricated real model ID.

This local synchronous fixture executes within the short write transaction.
It cannot be replaced with a network call in that transaction: future live work
must add durable pending/cancelled state, bounded provider timeouts, release locks
before I/O, and the approved call budget. That work requires a separate step.

## Verified behavior and limits

Final automated checks: **430 backend tests**, **67 frontend tests**, both
non-fixing frontend linters, and production build (47 modules) passed. Two
existing dependency deprecation warnings remain. Backend includes 25 new cases
covering retry/concurrency, stale contracts, schema migration, rollback, bounded
context, fallback sanitization, history pages, session association, travel-file
isolation, and request connections crossing worker threads. Frontend adds four
cases for routes, stable retries, duplicate blocking, and disposed/late replies.

An initial full run exposed a cross-worker SQLite close error. The connection
fix above and a deterministic regression case resolved it. Reverification of the
resource lookup changed the bundled review date; the corresponding resource
assertion was updated after it flagged the previous date. These are actual
observations, not invented model failures.

Browser checks used normal Vite at 5173 and the real FastAPI app through a
temporary standard-library HTTP/TestClient bridge at 8000 with temporary travel
and skills databases. Uvicorn protocol files remained cloud-only and startup
timed out, so ordinary Uvicorn startup was not reverified this turn. The bridge
adds no repository dependency/code; it runs the actual routes/storage. Live keys
were disabled and advisor providers replaced with functions that fail if called.
The temporary selector injected one malformed reply and a two-second delay for
explicitly named fictional fixtures only; production fixed_mock is unchanged.

Observed: failed request retained its draft; crisis dialog opened independently;
explicit retry saved an approved before-reply; rejected mock displayed the labeled
fallback; a pending mock was skipped without restarting/reopening conversation;
breathing started/stopped independently; optional after-reply used the approved
static-display fact; history restored after backend-process restart and reload,
with no automatic text preview. The late reply was visible only after opening
history. Travel matched Harbor Lantern Hotel (T001/T009); unmatched search
disabled stay selection. No booking or travel data was modified.

Evidence: [before reply](../evidence/assignment3-part2-conversation/before-reply.jpg),
[after reply](../evidence/assignment3-part2-conversation/after-reply.jpg),
[restored history](../evidence/assignment3-part2-conversation/restored-history.jpg),
[crisis during failure](../evidence/assignment3-part2-conversation/crisis-during-failure.jpg),
[curated fictional records](../evidence/assignment3-part2-conversation/records.json).
No real crisis service was contacted. No live-model selection quality, full
accessibility audit, new timing measurement, or peer evaluation is claimed.
No commit, push, upload, or submission was performed. Temporary QA services were
stopped; the user's pre-existing browser tab was preserved.


October 26 follow-up: normal Uvicorn startup subsequently succeeded during the
[display-preference step](assignment3-part2-preferences.md). Its schema v3 migration
preserves the conversation records and does not add preferences to mock context.
The earlier startup limitation above describes the conversation step's checks.


History-clear follow-up: schema v4 adds a pinned history_epoch to each turn.
Queued/retried old turns fail after confirmed clear and cannot recreate deleted
messages or runs. [Current contract](assignment3-part2-clear-history.md) supersedes
the earlier deletion-deferred scope; live-provider work remains unimplemented.
