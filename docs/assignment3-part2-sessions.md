# Assignment 3 Part 2 — Session storage and API

Implemented October 21, 2026. Scope: fictional session/event persistence and
history only. These endpoints never call a model or modify travel records.
They are mounted in the existing FastAPI app, using the existing backend setup.
There are no new dependencies or environment variables.

## Storage boundary

The first skills request initializes backend/instance/skills_prototype.sqlite3.
Travel startup does not need skills storage. Tests inject temporary paths; they
do not create or use the development database. Backend code rejects the travel
path, symlinks/hard links to it, foreign tables, partial schemas, corrupted files,
and unsupported schema versions. Skills storage failures do not stop travel
endpoints. Initialization now records version 4 in both PRAGMA user_version and
skills_metadata. The October 26 continuation explicitly migrates version 1,
preserving existing session records and adding conversation tables. The later
display-choice continuation migrates v1/v2 to v3 and adds preferences. See the
[conversation guide](assignment3-part2-conversations.md); future versions also
require explicit migration rather than recreation. See also the
[preferences guide](assignment3-part2-preferences.md).

Session tables are skills_metadata, skills_sessions, and skills_session_events. Sessions
store the fixed skill/version, explicit display settings, lifecycle/revision,
server timestamps, and client duration/progress checkpoints. Events store unique
IDs, ordered sequence, kind, timestamp, and the exact normalized request for retry
comparison. The original session step created no conversation/preference records; the
October 26 continuation adds isolated conversation records. No diagnostic or
inferred-distress records are created. No records expire or change merely because time passes.

## Endpoints

| Method and path | Behavior |
| --- | --- |
| POST /api/skills/sessions | Create ready session: 201 new, 200 exact retry, 409 same ID/different settings. |
| POST /api/skills/sessions/{session_id}/events | Atomically append one ordered event and update session, or return its existing event on exact retry. |
| GET /api/skills/sessions | Newest-first session history, limit 1–50, optional opaque cursor; returns sessions and next_cursor. |
| GET /api/skills/sessions/{session_id} | Saved session and ascending events, limit 1–50 and optional after_sequence; returns next_after_sequence when more exist. |

Create a fictional session with a client-generated UUID:

```json
{
  "session_id": "b74ba181-fecb-482f-97c9-00e92c2385e3",
  "display_settings": {"simpler_view": false, "motion_mode": "system"}
}
```

Display settings default to the values above. Motion mode may also be static or
gentle; it does not change a global preference. The backend supplies skill ID
paced_breathing_4_6 and skill version 1; clients cannot invent another skill or
change its inhale/exhale duration. Unknown body fields are rejected.

Start with an event shaped like this (example, not measured exercise evidence):

```json
{
  "event_id": "d707f13c-6726-47bc-8965-ae19491678aa",
  "sequence": 1,
  "expected_revision": 0,
  "kind": "start",
  "snapshot": {
    "active_ms": 0,
    "pause_ms": 0,
    "support_ms": 0,
    "setup_ms": 1000,
    "cycles_completed": 0,
    "phase": "inhale",
    "phase_remaining_ms": 4000
  }
}
```

Response keys are session, event, and replayed. Creation returns session and
replayed. The next event uses sequence 2 and expected_revision 1. Generate a
different event UUID for each new event; an exact retry retains the original
body, UUID, sequence, and expected revision. An old retry returns the existing
event alongside the **current** session; it cannot roll state backward. Duplicate
event IDs with changed data, stale revisions, and out-of-order sequences return
409. Fetch current detail to resolve a conflict; do not silently overwrite it.

Each event snapshot requires all seven fields above. Millisecond counters are
strict nonnegative integers bounded to JavaScript's safe integer range; booleans,
numeric strings, and fractional values are not accepted as integers. Setup time
is fixed after start. Progress/durations cannot go backward; paused time cannot
advance active progress. Excluded time is accounted according to whether the
support panel was open, and may not be relabeled as active time.

## Lifecycle and user control

- start: ready to running, with zero active progress and support panel closed.
- checkpoint: update progress/duration while running or paused without changing
  lifecycle. A paused checkpoint cannot advance exercise progress.
- pause: running to paused; optional reason is user, hidden, or timing.
- resume: paused to running only after the support panel is closed.
- support_open/support_close: opening during running pauses; closing does not
  resume. Opening from ready never starts. Support and ordinary pause time remain
  separate. The future support panel itself must work even if this write fails.
- stop: any nonterminal state to stopped, without an explanation or completion
  requirement. Stop/Leave in the future UI must take effect locally before
  awaiting persistence.
- complete: running to completed with six cycles, final exhale at zero remaining,
  and at least 60,000 active milliseconds. A longer duration is retained; beyond
  90,000 ms it is marked outside the duration limit, not forcibly discarded.
- interrupt: any nonterminal state to interrupted, for explicit page/refresh
  reconciliation. GET requests never interrupt or resume a session, avoiding
  mutation of another active tab merely because history is opened.

Terminal states reject new events. Exact previously accepted retries are still
safe. All updates and event insertion occur in one short write transaction;
concurrent updates at the same revision have one winner. An insertion failure
rolls back the session update, and no event is partially accepted.

The API checks reported consistency, not whether a person followed a cue or
whether all twelve phases were rendered. Every session response labels timing
as client_reported and timing_verified false. within_duration_limit is only a
derived completed-session duration flag, not independent verification or a claim
of clinical effect. UI/browser timing evidence remains future work.

## Errors and history guarantees

Malformed/unknown request fields return 422; invalid cursors return sanitized
400; missing sessions return 404; lifecycle/revision/idempotency conflicts return
409; storage initialization, lock, or SQLite failures return sanitized 503.
No response includes a database path, raw SQLite error, hidden prompt, provider
credential, or travel record. History performs only application-owned queries
with bound values and has bounded pages. Loading history makes no model call.

Existing records persist across new connections and fresh FastAPI application
instances against the same file. Actual server-process restart and frontend
refresh behavior have not yet been observed in a browser. No application service
was started for these tests. See [verification](assignment3-part2-verification.md).


## History-clear generation boundary

The subsequent [history-clear step](assignment3-part2-clear-history.md) adds
history_epoch to creates/events and session detail. Pin it from GET
/api/skills/history when beginning new activity; never replace it on retry.
Legacy missing fields mean epoch 0 and fail after the first clear. Schema v4
preserves older records on migration and only removes history on confirmed DELETE.
