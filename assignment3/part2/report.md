# Assignment 3.2 — Part 2 report draft

**Approved checkpoint source report — October 27, 2026.** Core Part 2 behavior
has verified evidence, including four fictional OpenAI checks on October 26.
The student approved this report and its documented limits and authorized the
Part 2 checkpoint/publication. Mock mode remains enabled. This committed source
report cannot name its own eventual commit: the separate upload-ready copy,
generated afterward, will supply the actual checkpoint SHA and absolute pinned
links. Do not upload this PENDING/local-link source copy.

Repository: [NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel).
Working branch: codex/assignment3-part2-foundations.

**Submitted version commit: PENDING — no Part 2 checkpoint has been created.**
Current HEAD e871cadc06d46398709d688df41de350d71c7f5b is the earlier Part 1
checkpoint, not the implemented Part 2 version. Implementation, this report and
evidence remain local/uncommitted. The source fingerprint below is not a commit.
The relative links in this draft must become accessible absolute commit-pinned
links after an authorized final checkpoint; this file is not ready for Canvas.

## Implemented scope and ownership

The Vue skills view is separate from Hudson Travel and uses its own SQLite file
through FastAPI /api/skills routes. The chosen skill is six cycles of four-second
inhale/six-second exhale. The application owns the fixed sequence, timer,
navigation, pause/resume/stop/leave, and resource controls. Conversation is optional
before or after; no typing, rating, or model wait is required during breathing.

A restrained cue has a static alternative and reduced-motion precedence. Optional
Save display choices/Use last setup/Reset actions preserve user choice: reading
saved preferences never applies them, reuse never starts breathing, and reset
keeps history. History shows participation and saved software checkpoints, not
improvement. Confirmed history clearing preserves display choices/travel/the allowance ledger and
uses persistent generations to reject older queued/retried writes.

SQLite schema v5 stores sessions/events, conversations/messages, explicitly
labeled mock/live run states, cancellation controls, a durable allowance ledger, a saved display-choice singleton and a history-clear receipt/
generation. Reviewed reply/fact IDs, visible text, timestamps and version/hash
metadata support review. It is plaintext local coursework storage without
accounts; only fictional inputs are appropriate. An unacknowledged draft or queue
can be lost on close; refresh never silently resumes pacing.

Actual reuse: the Vue/FastAPI layout and entry point, existing HTTP/error helper,
state-injection/test patterns, SQLite transaction/history ideas, and the travel
component retained through separate navigation. Skills storage, timing and reply
contracts are new. Hotel SQL generation, hotel data/prompts and maps do not supply
the skills conversation. No external clinical conversation dataset was used.

## Model contribution — four verified live checks, mocks restored

The default selector is **local-fixed-fixture-v1**, mode mock. It only branches
on before/after placement. It receives a reviewed catalog and bounded context
but does not interpret the fictional message or history. Before returns the
available-exercise/typing/pause facts; after returns an acknowledgment/static
option. This tests integration and response enforcement, not an actual model's
contribution or selection quality. Earlier hotel-chat model calls are not skills
model evidence.

The approved renderer rejects unknown IDs, incompatible/duplicate facts, extra
prose and malformed output. It renders approved application text or a fixed
fallback. There is no clinical detector or crisis classification gate; the mock
does not recognize crisis-related messages. Independent U.S. resources remain
available regardless of text, mock output or backend availability. The live model
selected the reviewed signpost in its fictional check; it must not supply individualized therapeutic
advice, change pacing/preferences, or hide support.

The student authorized four real OpenAI `gpt-6-luna` checks within the durable
ten-call/$1 allowance. Typing, motion choice, unsupported diagnosis/prescription
and a fictional support-reference message all returned HTTP 200/completed live
runs with the expected reviewed reply/fact selection. The unsupported request
followed the typing turn in the same conversation. The after-placement motion
case had no associated exercise session; no new exercise completion is implied.
All four returned model ID `gpt-6-luna`, with no distinct snapshot supplied.

The adapter used versioned instructions/bounded context, strict response validation,
three-second deadlines and durable pre-dispatch reservations. Provider-reported
usage totaled 2204 input/329 output tokens; actual billed cost was not inspected.
Four attempts reserved $0.40, leaving six calls/$0.60 of conservative allowance.
There were no failed live attempts or retries. Mock mode was restored, .env and
travel bytes were unchanged, preferences stayed unchanged, and new SQLite/history
reads restored all four runs/eight messages across three conversations.
See [method, results, limits and evidence](../../docs/assignment3-part2-live-checks.md).

These actual HTTPS provider calls used the application route in a headless local
harness, not a live browser session. Each scenario ran once. This supplies basic
model-contribution evidence; it is not the fifteen-case/repeated-variation Part 3
evaluation, a clinical assessment or a reliability guarantee. No additional live
calls are authorized by the current results. The app is back in default mock mode.

## Research reasoning and tradeoffs

R1 motivates a bounded short sequence; R2/D4 keep support visible even in failure
and confirmation dialogs. R3/R4 motivate immediate exit without penalty, optional
conversation and explicit Start/Resume/reuse. D1 is a manual simpler view because
the study establishes no reliable distress detection. D2/D3 motivate one phase at
a time, no required typing/disclosure, and no mandatory reflection/rating. D5
uses explicit saved setup rather than inferring feelings or benefit; the extra
Save click makes persistence clear but costs an action. D6 motivates neutral
language, muted presentation and static/reduced-motion pacing.

One skill limits choice; finite replies limit expression and may be inappropriate
when selected poorly. Structure validation cannot prove intent interpretation or
clinical safety. The simpler ready view retains optional conversation and Save/Reset controls,
contracting less than the original sketch. This preserves discoverability/control
at the cost of more visible choices; the student accepted this limited Part 2 tradeoff on October 27.
Live cancellation copy also mentions reviewing saved statuses, while history shows
message provenance/fallback rather than exact run-status badges. The API/SQLite
retain those states; those badges are not implemented. The full R/D mapping and remaining design
tradeoffs are in the readiness review and approved experience notes.

## Verified results

Most recent unchanged-source regression gate after the live checks: **492 backend
tests, 85 frontend tests, both linters and production build passed**. The final
documentation/UI review did not repeat these identical suites. Two existing backend dependency deprecation warnings
remain. Tests use temporary databases/mocks; no dependency was installed/upgraded.

An earlier verified Part 2 production-preview browser run completed all 12 ordered DOM phase cues
and six cycles in **60.011 seconds DOM-observed active time**; the clock/session
record was **60.010 seconds**, with **12.055 seconds setup** separately. No pauses,
support time, typing, or conversational calls occurred inside that run. It met
the intended <=90-second duration in this sample. Setup means ready-view/engine
creation through Start; initial page/asset loading was not measured. DOM updates
are not hardware-paint telemetry, and actual per-phase jitter/device variation
is unmeasured. The browser was visible and used static pacing.

A prior development run saved 60.014 seconds clock time but reloaded before DOM
capture. Its rendered interval is unknown. The production-preview repeat is the
reported measured sample; the two are not combined or presented as a software fix.

Browser/database inspection also verified before/after mock conversation,
malformed-output fallback, genuine backend outage with retained draft/error,
independent crisis access/Leave, pause/support return remaining paused, explicit
resume, Stop and active Leave. After a real backend restart/reload, four sessions,
three conversations, eight messages and four mock runs restored; one mock run
was deliberately rejected. That earlier evidence used mocks. In the final no-call review, the actual saved
live typing/follow-up and motion replies were also restored in browser history,
labeled Reviewed model selection, using a read-only server with providers and
write requests blocked. A separate temporary-database browser check repeated
malformed fallback, support/Back staying paused, Resume/Stop and genuine backend
outage with retained draft, support and immediate Leave. No additional live calls
or original skills-database changes occurred. Adapter unit tests use simulated
live-mode requests with MockTransport in separate temporary databases.
SQLite integrity/foreign keys
passed; development database hashes stayed unchanged. Matching/unmatched hotel
searches remained usable. No crisis service was contacted.

## Design and evidence links — valid locally; pin after checkpoint

- [Approved experience and complete research rationale](../../docs/assignment3-part1-experience.md)
- [Approved technical design](../../docs/assignment3-part1-technical.md)
- [Readiness matrix, integration observations and exact remaining steps](../../docs/assignment3-part2-readiness.md)
- [Earlier measured guided timing](../../evidence/assignment3-part2-readiness/timing.json)
- [Earlier completed exercise](../../evidence/assignment3-part2-readiness/completed-current-build.jpg)
- [Restored session](../../evidence/assignment3-part2-readiness/restored-session.jpg)
- [Restored conversation and fallback](../../evidence/assignment3-part2-readiness/restored-conversation.jpg)
- [Network failure](../../evidence/assignment3-part2-readiness/network-failure.jpg)
- [Support with backend offline](../../evidence/assignment3-part2-readiness/support-backend-offline.jpg)
- [Curated fictional database records](../../evidence/assignment3-part2-readiness/records.json)
- [Verified four-case live-model check](../../docs/assignment3-part2-live-checks.md)
- [Curated live batch](../../evidence/assignment3-part2-live-checks/batch.json)
- [Current adapter source fingerprint](../../evidence/assignment3-part2-adapter/source-manifest.json)
- [Final no-call UI/record verification](../../evidence/assignment3-part2-final-review/review-verification.json)
- [Actual live reply in history](../../evidence/assignment3-part2-final-review/live-history.jpg)
- [Observed simpler-view difference](../../evidence/assignment3-part2-final-review/simpler-view.jpg)
- [Final failure/support check](../../evidence/assignment3-part2-final-review/offline-support.jpg)
- [Checkpoint/evidence/manual submission checklist](../../docs/assignment3-part2-submission-checklist.md)
- [Preference verification](../../docs/assignment3-part2-preferences.md) and [clear-history verification](../../docs/assignment3-part2-clear-history.md)
- [Curated AI/process evidence](../../evidence/assignment3-part2-log.md) and [AI-use disclosure](../../AI-USE.md)

No Assignment 3 recording exists. The final demonstration/process screencast and
code explanation are Part 3 work; a short Part 2 walkthrough can be added if
required by the instructor/chosen to strengthen its demonstration. An older
Assignment 2 video is not evidence for this milestone.

## Remaining work and submission condition

The final readiness review is complete, and the student approved the documented
simpler-view, history-status-copy and timing/setup limits on October 27.
Mock-only checkpoint checks again passed 492 backend/85 frontend tests, lint/build.
The student authorized creation/publication of the
Part 2 checkpoint, then record its real commit and replace local evidence links
with absolute commit-pinned URLs verified accessible to the grader. Do not use
the Part 1 HEAD as the Part 2 submitted version.

Part 3's formal fifteen-scenario/live-variation evaluation, final recordings,
clean-checkout verification and full refinement remain separate unfinished work.
The provisional 250 ms cue-delay threshold lacks empirical phase-jitter validation.
Screen readers/full accessibility, OS motion toggling, external crisis handlers,
cold offline load and multi-device timing are untested; no clinical effectiveness
is claimed. Live was enabled only for the four authorized fictional checks and restored to mock.
Nothing was committed, pushed, uploaded or submitted.
