# Assignment 3.1 — Technical design

Updated: October 12, 2026.

Status: documentation proposal only. No new application code, tables, routes,
provider calls, or timing tests have been implemented. The student selected
60-second paced breathing and optional conversation before/after the exercise.
See the [experience design](assignment3-part1-experience.md) and
[requirements plan](assignment3-part1-plan.md).

## Architecture and ownership

The student confirmed a separate skills view in this repository, served by the
existing Vue and FastAPI applications, with its own SQLite file. Keep the FastAPI
entry point at backend/app/main.py and mount skills routes under /api/skills.
The existing hotel workflows and instructor CSV inputs remain separate.

Vue owns the visible breathing state machine and monotonic exercise clock.
FastAPI validates requests, retrieves approved context, stores records, invokes
the selected model, and validates its response. SQLite stores fictional session
and conversation history plus explicit preferences. Reviewed static skill and
crisis material belongs to the application, not generated database content.

The model has no tool for executing SQL, changing preferences, driving the timer,
starting/stopping exercises, or choosing navigation. The application performs
all reads through predefined parameterized queries. A displayed model reply is
conversation content, never an application command.

## Proposed records

Use backend/instance/skills_prototype.sqlite3, ignored by Git. Never copy travel
records into it. Proposed identifiers are generated UUIDs, timestamps are UTC
ISO strings, and durations are nonnegative integer milliseconds. Local history
is plaintext SQLite, not an encrypted or authenticated personal health record.
Only fictional messages belong in it. No accounts or diagnoses are proposed.

| Table | Main fields | Purpose and constraints |
| --- | --- | --- |
| skills_metadata | key, value | Schema version and migration bookkeeping; no travel CSV seeding. |
| skills_preferences | singleton_id, simpler_view, motion_mode, last_setup_json, updated_at | One local browser/device setup for coursework. Motion mode is system/static/gentle. Only explicit actions change preferences. Default respects reduced-motion settings. |
| skills_sessions | session_id, skill_id, skill_version, status, created_at, started_at, ended_at, active_ms, pause_ms, support_ms, setup_ms, cycles_completed, display_settings_json, revision | Status is ready/running/paused/completed/stopped/interrupted. Skill ID is paced_breathing_4_6. Completed means the planned sequence ended, not that it helped. Versioned configuration fixes 4000/6000 ms phases and six cycles. |
| skills_session_events | event_id, session_id, sequence, kind, created_at, active_elapsed_ms, phase, phase_remaining_ms | Ordered start/pause/resume/support-open/support-close/stop/complete/interruption checkpoints. Unique session/sequence and event ID prevent duplicate writes. Update local stopped state before showing any persistence error. |
| skills_conversations | conversation_id, session_id nullable, placement, created_at, updated_at | Placement is before/after/standalone. Nullable session association supports optional conversation before starting an exercise. |
| skills_messages | message_id, conversation_id, sequence, role, content, source, created_at, reply_id nullable, skill_version nullable | Ordered visible fictional messages; role is user/assistant. Source distinguishes user/model-selected-template/application-fallback. Unique conversation/sequence; user text at most 500 characters. |
| skills_model_runs | run_id, conversation_id, user_message_id, request_id, status, mode, model_id, prompt_hash, context_version, selected_reply_id nullable, error_category nullable, created_at, ended_at | Pending/completed/failed/cancelled record; mock/live mode and model identifier separate evidence. No key, authorization header, raw provider error, or hidden reasoning. Request ID is unique for duplicate protection. |

Use foreign keys and cascading deletion for conversation messages/runs and
session events. A conversation's optional session reference uses SET NULL when
only a session is deleted, so standalone conversation history is not silently
destroyed. Clearing all history deletes both sessions and conversations.
Enforce status/enum, phase-time bounds, ordered sequences, and JSON size limits
in backend validation and relevant SQLite constraints. Do not store emotional
scores, diagnoses, inferred distress, location coordinates, or crisis-panel text
as user data. Event timestamps support software review, not crisis surveillance.

Begin/commit short transactions around record changes. Release the database
connection before waiting for the provider; do not hold a write lock during a
model request. Use a schema version with explicit migrations rather than merely
assuming CREATE TABLE IF NOT EXISTS upgrades existing tables.

## History, preferences, and deletion

Session history shows date, skill, status, and active duration, with pause/setup
durations available on expansion. Conversation history opens the visible
messages on demand. No message preview appears automatically on entry, and
loading history never triggers a model call. Fetch at most 50 summaries per page
using an opaque cursor; fetch conversation messages in pages of at most 50.

Remember simpler-view and motion choices when the user changes those controls.
Remember the last explicitly selected setup without marking it as preferred or
effective. Offer "Use last setup"; do not auto-start or select it invisibly.
No inference from a completed session or model reply updates a preference.
Because this version has one skill, personalization primarily adapts display
choices rather than recommending different exercises (D5/R4 limitation).

Provide separate Reset display choices and Clear saved history actions. Clearing
history gets one concise confirmation because deletion is permanent; Stop/Leave
never require confirmation. Resetting preferences does not delete conversations.
The coursework device is single-user; multiple browsers share the same backend
history. Warn in setup documentation that local does not mean private from other
users of that computer. Do not present this design as production privacy support.

Before clearing history, invalidate pending runs so their late responses cannot
recreate deleted messages. Any completion transaction must find the original
pending run and matching revision; missing/cancelled records are not recreated.

## Relevant context and model response boundary

Use a reviewed prompts/skills-assistant.md instruction file and a versioned
backend/app/skills/context.json skill definition. The context contains the
approved 4–6 sequence, six cycles, available controls, coursework limitations,
and a finite catalog of neutral conversation replies. This is application-owned
retrieval of relevant context, not model-generated SQL or an external clinical
dataset. No external conversation dataset is required for this assignment.

Each optional conversational turn contains:

1. Versioned model instructions and approved skill/reply catalog.
2. Current placement (before/after) and, if associated, skill/status facts from
   a predefined query. Never interpret participation as improvement.
3. Explicit presentation preferences needed for the reply, excluding unrelated
   history and identifiers not needed by the model.
4. Up to six prior visible messages in this conversation, bounded to 3000 total
   characters, then the new normalized fictional message of at most 500.

Trim history oldest-first while preserving role ordering. Stored user messages
are untrusted content, not instructions. Do not use cross-conversation retrieval
by default. Tell the fictional user before Send that text is stored locally and
sent to the configured provider; never claim provider handling is identical to
local-only storage. The eventual integration must document actual provider
configuration and verify supported request settings using current documentation.

Propose a strict structured response with exactly reply_id and fact_ids. The
reply_id must be from a reviewed catalog, such as neutral_acknowledgment,
explain_available_skill, clarify_supported_scope, or support_signpost. fact_ids
is a bounded list of approved facts, such as inhale_four/exhale_six,
six_cycles, pause_or_stop, or fictional_testing_only. The server renders only
their approved text, at most three short sentences and 600 characters. The
provider supplies no freely rendered therapeutic prose, HTML, URLs, timer
values, navigation commands, or preference updates.

Example contribution: for a fictional question about typing during the exercise,
the model selects explain_available_skill with the approved no_typing_required
and pause_or_stop facts. After a fictional statement about disliking motion, it
can select an acknowledgment and approved static_display_option fact. The UI
still requires the user to change the setting. The model uses relevant context
and prior conversation to select a concise response; it does not merely echo a
fixed welcome message.

Tradeoff: finite replies greatly constrain invention and tone, but conversation
will be less expressive and may misunderstand the intent. Structured validation
enforces permitted content, not correct interpretation or clinical safety.
Live variation checks must examine inappropriate fact/template selection.
Unsupported requests receive a reviewed scope reply. The student should review
whether this bounded contribution is sufficient for the course expectations.

Validate exactly one response object, allowed keys/enums, fact compatibility,
deduplicated facts, size, and completeness. Reject extra prose or arbitrary
fields. Missing/malformed/incompatible output creates a safe failure and fixed
fallback, not an assistant success record. Store rendered text, reply ID, model
identifier, mock/live flag, prompt hash, and context version for reproducibility.
Do not store raw rejected output. Exact schemas and provider request settings
will be specified and verified before implementation.

## Crisis input and independent access

Do not propose a clinical distress detector, risk score, or automatic routing.
The model instruction for fictional crisis-related messages requests a concise
support_signpost response, whose text is application-reviewed and points to the
always-visible Crisis support control. It makes no claim of monitoring or
assessment. This may misclassify or miss an input; evaluate that limitation with
fictional cases. A system prompt or model selection is never the support gate.

Bundle the independently rendered support panel and verified resource data with
the frontend. Access must not depend on a backend fetch, model response, message,
classifier, or initial setup choice. Record source URLs, geographic scope, and
last verification date with the resource data when actual resources are chosen.
The student selected U.S. scope; [resource notes](assignment3-part1-resources.md)
record listed contacts and verification limits. External destinations need connectivity even when
the local panel does not. Crisis access pauses pacing and never resumes it
automatically. Do not record what external resource the fictional user opens.

## Timing and lifecycle implementation proposal

Use a small pure JavaScript state machine with an injected monotonic clock for
tests. States are ready/inhale/exhale/paused/completed/stopped. Use elapsed
performance time for phase calculation rather than counting interval ticks.
Rendering updates can use requestAnimationFrame, but the elapsed clock is the
authority. Unmount/stop cleans up scheduled callbacks and event listeners.

Start the active clock when the first Inhale cue is rendered. Phase boundaries
are 4, 10, 14, 20, 24, 30, 34, 40, 44, 50, 54, and 60 seconds; there is no hold
or provider wait between them. Track actual rendered transitions separately
from planned deadlines so delayed cues are detectable. Finish at the rendering
of the completion view after the last exhale. Do not clamp an observed value to
60000 or report the planned schedule as measured evidence.

On Pause or document visibility loss, freeze the active elapsed time and retain
phase/remaining time. Resume excludes the pause interval. Time spent with Crisis
support open is tracked separately from other pause time, with mutually
exclusive interval categories to avoid double counting. Wall time minus these
excluded intervals gives active measured duration, including active rendering
delays. Record entry/setup until first instruction separately. User response
assumption: press Start when ready; no response is required inside the sequence.

If rendering stalls enough to skip a phase, pause and report a timing
interruption rather than presenting catch-up cues or claiming a valid completed
sequence. Verify all twelve phases displayed, actual duration at most 90000 ms,
and approximate 4/6 phase timing. The acceptable per-phase jitter is an open
measurement decision; do not pick a tolerance merely to make a failed run pass.

Send ordered state-change checkpoints without awaiting network completion to
show cues or stop them. Sequence/revision numbers reject stale writes. On
refresh, restore saved history without replaying motion. A nonterminal record
from the prior page becomes interrupted on reconciliation, never completed.
Do not promise exact active time after a crash: the last acknowledged checkpoint
is a lower bound and should be labeled incomplete.

If persistence is down, the local exercise may proceed with a visible "Not
saved" indication. Do not silently replay writes on reload or show a volatile
session as persisted. A future explicit Save again action may resend a bounded
session snapshot with the same ID; its contract needs implementation review.

## Proposed API contracts

All names below are proposals, not available endpoints. Inputs use strict enums,
bounded strings, validated IDs, and parameterized SQL; responses never contain
credentials, database paths, hidden instructions, or raw provider errors.

| Endpoint | Purpose |
| --- | --- |
| POST /api/skills/sessions | Create an idempotent ready record with skill version and display snapshot. |
| POST /api/skills/sessions/{id}/events | Append ordered idempotent lifecycle checkpoint and update status/duration in one transaction. |
| GET /api/skills/sessions | Paginated session summaries. |
| GET /api/skills/sessions/{id} | Review one session and acknowledged checkpoints. |
| POST /api/skills/conversations | Create a before/after/standalone conversation. |
| POST /api/skills/conversations/{id}/messages | Persist the user message/pending run, make one optional model call, then validate and save visible reply. |
| GET /api/skills/conversations | Paginated conversation summaries without unsolicited message previews. |
| GET /api/skills/conversations/{id} | Restore visible messages and safe statuses without a new model call. |
| POST /api/skills/runs/{id}/cancel | Cancel a pending turn when leaving; best effort, with late-result UI guards regardless. |
| GET /api/skills/preferences | Load explicit presentation defaults. |
| PATCH /api/skills/preferences | Change only explicitly requested allowlisted preferences. |
| DELETE /api/skills/preferences | Reset display choices. |
| DELETE /api/skills/history | Clear sessions/conversations and invalidate outstanding runs transactionally. |

Repeated request IDs return the existing pending/completed/failed run, never a
second provider call. Explicit retry uses a new request ID linked to the failed
turn, without duplicating its visible user message. A cancelled frontend fetch
does not guarantee cancellation of a provider call already sent. Pending runs
left after backend restart become failed/interrupted without automatic retries.

## Failures and bounded calls

| Case | Required application behavior |
| --- | --- |
| Invalid/blank message | Local and backend validation; no provider call and no new message/run. |
| Missing key/model configuration | Safe conversation-unavailable response; breathing and bundled support remain usable. |
| Provider timeout, authentication, rate limit, or malformed response | Finite timeout, sanitized category, fixed fallback, explicit retry only. |
| Duplicate Send | One in-flight turn per conversation and unique request ID; no automatic paid repeat. |
| User starts breathing/leaves during a turn | Invalidate view request generation; late reply cannot navigate or replace current state. A cancelled or discarded result is marked appropriately. |
| SQLite unavailable before Send | Do not send a live call whose required record cannot be saved. Offer the independent exercise. |
| Save fails after a provider result | Report persistence failure; no automatic repeat call. Do not label reply as saved. |
| History loading fails | Show a bounded error instead of another conversation's stale messages. No model call. |
| Preference saving fails | Use current in-memory display choice with a "Not saved" indication; no hidden default overwrite. |
| Tab hidden, refresh, browser close | Pause or restore interrupted status; never auto-resume or infer completion. |

Default development and peer testing to mock mode. Live mode requires explicit
host selection, uses the existing backend-only credential pattern, and has a
backend-enforced budget of at most fifty calls per peer-testing session. Count
every dispatched attempt, including failed/cancelled attempts, before dispatch.
At the limit return to clearly labeled mock mode; do not reset the budget on
refresh or restart. Technical implementation of durable test-session counters
will be specified before live testing. Make no live calls in Part 1.

## Proposed code organization and concrete reuse

Keep the current entry point and add backend/app/skills/ modules for routes,
schema/storage, contracts, context loading, and provider handling. Put the new
tests under backend/tests/skills/. Use frontend/src/components/skills/ for a
SkillsExperience container, BreathingExercise, CrisisSupportPanel,
SkillsConversation, and SkillsHistory; place the pure timing module and its
tests under frontend/src/skills/. Add frontend/src/api/skills.js and API tests.
Bundle resource data in frontend/src/skills/crisisResources.js. Use an explicit
app switch/view without adding a routing dependency unless later justified.

| Existing file/pattern inspected | Planned reuse | What changes |
| --- | --- | --- |
| backend/app/config.py | Backend-only .env loading and safe configuration checks. | Separate skills mock/live setting and database path; no Vue credential. Final environment names need documentation. |
| backend/app/openai_client.py | httpx transport injection, finite timeout, strict response parsing, sanitized errors. | New skills client/response contract and one conversational call; remove hotel query/answer stages and pricing assumptions. Verify provider support before implementation. |
| backend/app/advisor_history.py | Short transactions, ordered messages, bounded history, durable run status. | Skills tables and identifiers, cancellation/idempotency/deletion rules; adapt the pattern rather than calling hotel storage. |
| backend/app/database.py | sqlite3 foreign-key/transaction patterns. | Separate schema initializer with no CSV loading or travel-table changes. |
| frontend/src/api/http.js | Existing shared requestJson and friendly JSON/error handling. | Skills-specific API methods; add cancellation support where necessary rather than assuming it already exists. |
| frontend/src/components/HotelAdvisor.vue | Vue refs, explicit loading/errors, history restore pattern. | New focused components; no global busy state that disables safety/leave, no automatic latest-chat disclosure, no SQL evidence in the skills UI. |
| backend/tests/conftest.py and provider tests | Temporary databases, injected dependencies, mocked httpx responses. | Isolated skills fixtures; never use the development DB or paid calls for routine tests. |
| frontend/package.json | Existing Vue/Vite/lint/build and node:test tooling. | Add pure state-machine tests to the test discovery command later; current discovery covers only src/api/*.test.js. No dependency installation is proposed. |

These are planned adaptations, not a claim of code already reused. Existing
packages appear sufficient for this scope. Do not copy hotel prompts,
model-generated SQL, Geoapify/Leaflet interactions, booking semantics, or travel
data into the skills prototype.

## Verification plan and limits

Automated mocked checks will cover the exact skill sequence, timing with an
injected clock, pause/support exclusions, skipped-phase interruption, idempotent
writes, response allowlists, history restoration, deletion with pending runs,
and preference changes requiring explicit user action. Use temporary databases.
Frontend tests must include state transitions in addition to API contracts.

Browser evidence must measure actual cues and completion, test keyboard and
reduced motion, inspect saved SQLite records, and verify visible crisis access
with the provider and backend unavailable. Live-model checks examine variation
in template/fact selection separately from deterministic mocked checks. These
checks establish software behavior, not therapeutic effectiveness. No check in
this plan has yet been executed against a skills application.

## Confirmed choices and remaining review

1. **Organization confirmed:** separate skills view/database in this repository.
   Working name: "Skills Prototype."
2. **Resource region confirmed:** clearly labeled U.S. information; contacts and
   remaining copy/navigation checks are recorded in the resource notes.
3. **Model contribution confirmed:** finite-template/fact selection. It trades
   flexible dialogue for stronger application control over visible content.
   Instructor expectations remain worth checking if open-ended generation is
   specifically required; no such requirement is stated in the supplied text.

Engineering decisions still to resolve during implementation: exact provider
schema support, clock jitter tolerance based on measurements, best-effort
persistence recovery, deletion/cancellation races, and durable live-test budget
records. Those do not block a Part 1 proposal if their limits are documented.

## Evidence for this step

The assistant inspected existing configuration, provider contracts/client,
SQLite/history code, Vue advisor/API helper, test fixtures, and dependency
declarations read-only. This document specifies proposed behavior and truthful
reuse candidates; it changes no application behavior or dependency declaration.
The student accepted the organization/resource/model choices. README/AGENTS
guidance, AI disclosure, evidence notes, and the Part 1 report are drafted.
The student supplied GPT-6.1 Sol with medium effort for the disclosure; desktop
version remains unavailable. The next action is student review, followed by a
reviewed submission checkpoint. See [readiness steps](assignment3-part1-readiness.md).
