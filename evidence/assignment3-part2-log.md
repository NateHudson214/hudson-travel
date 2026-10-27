# Assignment 3 Part 2 — Curated evidence

October 21, 2026. Only fictional scenarios and local mocks are used.

| Prompt/action | Evidence and decision | Limits |
| --- | --- | --- |
| Student requested the first implementation step, mocked responses, travel preservation, relevant tests, and the next exact prompt/action. | Reviewed the approved plan, experience, technical design, resource notes, and source/test setup; created a separate Part 2 branch. | Part 1 checkpoint preserved; no commit/push or live call in this step. |
| Chose pure timing and reply boundaries before UI/storage. | New session engine owns the fixed sequence. Mock output can select only approved reply/fact IDs; unknown prose/actions are rejected. | No running skills view, API, or SQLite records yet. |
| Revisited late-callback behavior from Part 1. | Explicit provisional 250 ms overdue threshold pauses and retains the prior phase rather than catching up; delays remain in active duration. | Virtual-clock tests cannot establish actual browser rendering or clinical appropriateness. |
| Fictional request/malformed-response tests. | Inject local response providers, including timeout and extra-prose cases; fallback is fixed text with no retry or raw error. | No provider traffic, distress detector, or verified live model behavior. |
| First reply assertion and correction. | Naive sentence splitting incorrectly counted "U.S." as extra sentences. Revised the test's boundary detection; 27 independent reply tests passed. | This was a test assertion defect, not a therapeutic output or model failure. |
| Interrupted verification and recovery. | Dependency import stacks and dataless metadata identified cloud-only files. Student selected Keep Downloaded and requested verification only. Fresh process inspection found no earlier task test processes remaining. | No installation/upgrade, next implementation step, or unrelated-process cleanup. |
| Resumed standard checks. | Backend: 355 passed with two existing warnings. Frontend: 51 passed, both non-fixing linters passed. Production build passed (28 modules); git diff --check passed. All resumed verification commands exited; no prior test processes required cleanup. | No dependency changes, implementation work, services, or live provider calls during this continuation; no browser timing claim. |
| Student authorized session/event SQLite persistence and lifecycle/history APIs. | Implemented separate lazy database initialization, strict session/event contracts, atomic ordered updates, replay/conflict handling, and paginated history. | No UI, preference/conversation storage, live calls, or dependency changes. |
| Chose explicit interruption events instead of mutating state on history reads/startup. | Reading history cannot stop another active tab. A later UI reconciliation step must explicitly report interrupted sessions. | Crash duration remains an acknowledged-checkpoint lower bound, not verified browser measurement. |
| Focused session checks. | 50 API cases passed using temporary SQLite files, including concurrent requests, a failed-insert rollback, locked storage, foreign schemas, and unchanged travel-file hashes. | Fresh application-instance persistence is verified; real browser/service-process restart is not. |
| Session-step regression gate. | 405 backend tests and 51 frontend tests passed; both non-fixing linters, the 28-module build, and diff check passed. Two existing backend deprecation warnings remain. | No dependency change, live model call, service, commit, or push. Skills UI/conversation persistence and measured browser duration remain unfinished. |

See [verification](../docs/assignment3-part2-verification.md) for test outcomes,
repeatable commands, unresolved implementation work, and the distinction between
simulated duration and measured browser duration. Do not include real distress
disclosures, credentials, or private source material in later evidence.

## Vue experience continuation — October 22, 2026

- Student requested a separate skills view using tested timer/session APIs,
  start/pause/resume/stop/leave/history, independent U.S. resources, reduced motion,
  regression tests, and the exact next prompt. No live calls were authorized.
- Preserved the travel component and connected the skills view through hash
  navigation/KeepAlive. Added ordered checkpoint saving and explicit retry;
  local exercise/support controls do not wait for backend responses.
- Reverified U.S. contacts using helpline lookup and the official Lifeline page;
  no call, text, or service chat was initiated.
- Observed twelve DOM cues over 60,004 ms, with engine 60,000 ms and setup 9,345 ms.
  This is one desktop run, not proof of hardware paint timing or effectiveness.
- A cold session-create request timed out; explicit retry succeeded. During a
  deliberate backend outage, a new exercise, crisis panel, and Leave remained
  usable; queued events saved after restart and explicit retry.
- Reload did not restart breathing. Explicitly marking an abandoned record
  interrupted initially updated detail but left the list row stale. Fixed the
  row update and recovery-marker cleanup; repeated UI review confirmed agreement
  and a cleared marker after reload. Unload saving remains best-effort.
- Static/simpler controls fit a 360×640 viewport; Escape restored crisis-button
  focus and left exercise paused. Device reduced-motion handling is unit-tested
  and backed by CSS; actual OS preference and screen readers were not exercised.
- Travel matched two Harbor Lantern Hotel records; a fictional unmatched query
  cleared stale results. Navigation retained the travel query and stopped pacing.
  Browser warning/error log was empty after these checks.
- Full backend: 405 passed, two existing warnings. Frontend: 63 passed, both
  linters and 42-module production build passed. No dependency changes, live
  model calls, commit, push, or submission. Detailed evidence/limits are linked
  from docs/assignment3-part2-browser-verification.md.

## Mocked-conversation continuation — October 26, 2026

- Student requested optional mocked before/after conversation, approved reply/fact
  rendering, separate SQLite history, preserved controls/crisis access, tests,
  and next prompt. No live calls were authorized.
- Added atomic user/reply/run pairs with exact request retries, bounded same-chat
  context, paginated on-demand history, explicit v1→v2 migration, and a finite
  local selector. The UI identifies mocks rather than claiming model understanding.
- Actual failed approaches: initial frontend command ran from repository root
  rather than frontend/ and was corrected. Cloud-only dependency reads stalled
  checks; the student finished downloading. Uvicorn protocol imports timed out;
  QA used a temporary standard-library HTTP bridge to the tested FastAPI app.
- Focused skills tests initially passed, then a full suite caught concurrent
  dependency teardown on a different SQLite worker. Enabled thread handoff for
  each request-owned connection and added a deterministic regression check.
  The corrected full suite passed 430 cases with two existing warnings.
- The refreshed resource review date tripped an old exact-date assertion;
  updated it to the newly verified lookup date. Final frontend: 67 tests, both
  non-fixing linters and 47-module build passed. No package was installed/upgraded.
- Browser observed retry success after initial unavailable backend, locally
  rendered crisis panel during failure, an injected malformed mock becoming
  labeled fallback, and a delayed reply ignored after choosing breathing.
  Saved history later contained the dispatched reply. Start/Stop and optional
  after-conversation worked; reply did not change motion/preferences.
- Restarted the temporary backend process and reloaded Vue; no messages appeared
  automatically, and explicitly opened history restored saved replies. Travel
  matched T001/T009 for Harbor Lantern Hotel and disabled stay selection for a
  fictional unmatched name. No travel writes or provider calls occurred.
- No new browser timing/clinical claim, full accessibility audit, live model
  quality evaluation, Part 2 report/submission, commit, or push. Evidence and
  current limits: docs/assignment3-part2-conversations.md.

## Explicit display-preference continuation — October 26, 2026

- Student requested saved display preferences, Use last setup, Reset display
  choices, optional reuse/no auto-start, preserved motion/crisis/travel behavior,
  no live calls, normal startup verification, tests, and next prompt.
- Added explicit save, nullable saved setup, local-only use, and local-immediate
  reset with separately acknowledged durable reset. Revisioned singleton/tombstone
  and serialized requests prevent stale saves from undoing reset. Schema v3
  migrates v1/v2 while retaining history. No model can write these choices.
- Normal Uvicorn startup succeeded with existing dependencies. The broad reload
  watcher reacted to ongoing dependency hydration; documented backend/app-only
  watch scope and verified normal startup/restart with that command and npm run dev.
  No ASGI bridge, provider override, alternate database, or dependency install.
- Browser observed saved simpler/static choices, default full/system on reload,
  explicit reuse with engine still ready, then separate Start/static pacing and
  crisis access returning paused. Stop persisted one fictional session/four events.
- Backend outage: Reset applied locally, failure disclosed saved copy may remain,
  crisis dialog and Leave worked. A stale clearing-progress notice persisted after
  failure; fixed it, added an assertion, and repeated the UI check successfully.
- After normal service restart, Refresh still offered the saved copy without
  applying it. Explicit reset cleared it; reload confirmed no saved setup.
  Repeated compact-view save/reuse/reset; row ended revision 4 with no saved setup.
- Final gate: 448 backend tests, 74 frontend tests, both non-fixing linters,
  50-module build, diff/local-link checks passed. Two existing warnings remain.
  History rows were unchanged by reset, and the travel DB hash was unchanged.
  Matching/unmatched hotel searches worked; no booking/model/provider action used.
- No live selection-quality/clinical/accessibility claims, new timing measurement,
  final report, commit, push, upload or submission. Normal QA services stopped.
  Full record: docs/assignment3-part2-preferences.md.

## Confirmed skills-history clearing — October 26, 2026

- Student requested confirmation, session/conversation clearing, protection from
  pending/retried writes, separate preferences, travel/crisis preservation, no
  live calls, temporary-database deletion tests, UI checks and the next prompt.
- Chose persistent generations rather than only cancelling client requests:
  cancellation cannot undo an already dispatched server write. Schema v4 retains
  a generation/clear receipt; all history writes check their pinned generation
  transactionally before insert/replay. Latest clear replay does not delete new
  activity. Missing generation state fails closed. Preference revision is separate.
- Added strict DELETE confirmation and a native dialog with Cancel/Crisis/Leave,
  loading/failure controls, in-memory queue disposal and stale-view invalidation.
  GET does not clear data; local breathing never depends on the status request.
- Verification commands issued in the root were corrected to frontend/. All
  final checks passed: 465 backend, 81 frontend, non-fixing linters, 53-module
  build, diff/local-link checks. Two existing dependency warnings remain.
- UI automation initially matched both crisis buttons, then used the dialog
  scope. A click after page reload found no dialog; inspected and reopened it.
  These were automation corrections, not claimed app/model failures.
- Cancel preserved the QA records. Crisis/Leave worked from confirmation. After
  Start/Pause, confirmed clear deleted two sessions/two events/one conversation/
  two messages/one run; all five tables were empty, epoch 1, preferences retained.
  Old-generation writes were rejected. No development history was deleted.
- New explicit mock conversation at epoch 1 saved and reloaded. Outage disabled
  deletion while keeping crisis/leave. Backend restart preserved epoch 1 and
  absence of original IDs; only new activity remained. Travel matched T001/T009
  and unmatched query cleared selection. QA travel/development file hashes stayed
  unchanged. Temporary services were stopped and user tabs retained.
- No live calls, dependency change, real crisis contact, new timing/clinical
  claim, final Part 2 report, commit, push, upload or Canvas submission.
  Details: docs/assignment3-part2-clear-history.md.

## Part 2 readiness review — October 26, 2026

- Student requested review against the full assignment/approved design, remaining
  mock integration checks, outstanding requirements including model use, a draft
  report, and exact steps; prohibited commit/push/live enablement/submission.
- Reviewed the entire supplied Pasted text.txt and design/code. Main finding:
  fixed_mock branches on placement only; passing replies/context/persistence do
  not demonstrate the Part 2 conversational model. Live adapter, durable live
  lifecycle/budget and actual contribution evidence are missing. Current HEAD is
  the Part 1 checkpoint; Part 2 implementation/evidence are uncommitted.
- Reran 465 backend/81 frontend tests, non-fixing linters and 53-module build;
  passed, with two existing warnings. No new dependency or app code change.
- Temporary QA began at generation 2 with a saved static/simpler setup. Before
  reply and explicit reuse worked; Start remained separate. First development
  run saved 60.014 s clock/42.305 s setup, but reloaded before DOM capture. Cause
  not established; did not infer a rendered duration. Repeated in production
  preview: 12 cues, six cycles, DOM 60.011 s, clock 60.010 s, setup 12.055 s,
  no pauses/support or conversational runs during either completed exercise.
- After-reply linked to completed session; injected malformed selection became
  fixed persisted fallback. Backend outage retained draft/error, local resources
  and Leave. Explicit pause/support return/resume/stop and active Leave worked.
  Service restart/reload restored four sessions, three conversations, eight
  messages and four mock runs (one deliberately rejected); no live runs.
- Travel matched T001/T009 and cleared unmatched selection. SQLite integrity/FKs
  and unchanged development DB hashes checked. Added a local source fingerprint,
  not a fabricated commit. No Assignment 3 video exists; older Assignment 2 video
  was not relabeled. Part 3 evaluation/recording/clean-checkout work stays separate.
- Draft report: assignment3/part2/report.md. Current criteria, caveats and exact
  next steps: docs/assignment3-part2-readiness.md. Current evidence under
  evidence/assignment3-part2-readiness/. No commit, push, live call or submission.

## Disabled skills-provider adapter — October 26, 2026

Student choices: OpenAI, gpt-6-luna, ten dispatched attempts/$1 total. Student
explicitly required disabled mode, default mocks and no real calls. Official
OpenAI documentation was checked; no account/model connectivity probe was made.
New schema-v5 migration preserves earlier data. Pending records and allowance
reservations commit before the provider wait; cancellation/clear-generation and
final-result checks prevent late resurrection. The ledger is retained on clear.
The composer displays the host mode before accepting a send and cannot silently
opt an older mock screen into live mode.

The first skills suite run found five failures from schema-v4 expectations and
legacy fixtures that retained newly added v5-only tables when simulating old
schemas. Updating those fixtures left two actual status-check failures: strict
integer validation on a URL query parameter rejected string query values. Using
a bounded Query integer resolved both. Full regressions and new race tests were
then rerun. No failure observation or model result was fabricated.

Browser verification used the actual app behind a temporary mock-only harness,
Vite and temporary databases. Before conversation showed mock-only disclosure,
saved the reviewed typing/pause reply, opened the independent support panel and
left to idle immediately. SQLite v5 integrity and foreign keys passed; its live
reservations remained zero. Both development databases matched their prior hash
snapshots. The initial local-port bind was blocked; the same test commands worked
after permission to open localhost ports. Test services/tabs were then stopped.
No existing 60-second measurement was relabeled as a new adapter timing result.

See [adapter guide](../docs/assignment3-part2-adapter.md),
[mock screenshot](assignment3-part2-adapter/mock-conversation.jpg) and
[curated browser records](assignment3-part2-adapter/browser-records.json).
Actual provider access, contextual selection, variation and billing remain
unverified. No commit, push, actual live enablement/call, upload or submission.

Final adapter regression gate: 492 backend tests and 85 frontend tests passed;
non-fixing oxlint/ESLint and the 53-module production build passed. The development
screen reset between later browser interactions for an unestablished reason. The
completed mock reply, support access and immediate Leave were repeated against
the built production preview; its screenshot replaces the earlier development
capture. No cause or application fix is inferred. The final temporary database
contains two completed mock runs, no live reservations, and passes integrity/
foreign-key checks. The source fingerprint is local and uncommitted.

## Authorized four-case live check — October 26, 2026 local time

Student explicitly authorized at most four real fictional checks within the
existing ten-call/$1 durable ledger. Official model/pricing pages were reopened;
preflight found schema v4/no live ledger yet, automatically migrated to v5 with
preserved session, then found zero reservations/live/pending runs. No counter was
reset. A single-use journal guarded the real-route/real-HTTPS harness; .env was
never edited and only its child process temporarily enabled live mode.

Four of four completed with expected IDs/facts: typing/no_typing_required,
motion/static_display_option, unsupported request/clarify_supported_scope, and
fictional reference/support_signpost. Actual route times were 2881, 2160, 1936
and 2793 ms; each provider HTTP status was 200 and returned model was gpt-6-luna.
No failed attempt, retry, service contact or hidden fifth call. Provider usage
reported 2204 input/329 output tokens; no billing-page inspection occurred.

SQLite stores four completed live runs/eight messages across three conversations;
new connections and history GETs restored the saved records. Ledger reservations
are 4/$0.40, leaving 6/$0.60. These are reservations, not billed charges. No pending
run, integrity error or foreign-key error remained. Preferences/history epoch,
travel hash and .env bytes were unchanged. The original source manifest matches.
Mock mode was restored and its HTTP status route independently verified false/
mock; no persistent live server was started or left running. Full mock backend
492/frontend 85, linters and 53-module build passed again. This step changed no
application source or dependencies and made no commit/push/submission.

See [live-check guide](../docs/assignment3-part2-live-checks.md),
[curated batch](assignment3-part2-live-checks/batch.json) and
[independent verification](assignment3-part2-live-checks/verification.json).
The final readiness review, reviewed checkpoint/publication, commit-pinned links
and grader access still remain; Part 3 broader evaluation remains separate.

## Final Part 2 readiness review — October 27, 2026

Read the complete assignment, current report/evidence and approved design. Basic
actual model contribution is now evidenced by the four authorized checks, unlike
the earlier review's missing-model blocker. Current source fingerprint matches the
492-backend/85-frontend lint/build gate; no identical full-suite rerun was needed
for a documentation-only review. No new provider call or dependency/source change.

Final production-preview mock UI checks confirmed: simpler view hides history and
explanations but retains optional chat and Save/Reset; malformed fixture returns
fixed fallback and never stores unapproved fixture text; support opens during
breathing and Back stays paused; explicit Resume/Stop works; genuinely stopped
backend leaves draft/error and independent support/Leave usable. No retry was
invoked. A read-only GET-only/provider-disabled backend then showed actual saved
live typing/follow-up and motion replies labeled Reviewed model selection. The
original skills DB hash remained unchanged; its four completed live runs/reserved
$0.40 remain, with no pending runs and six/$0.60 left. No service contact.

The final review flags rather than silently fixes simpler-view contraction and
history-status-copy differences, setup/jitter/threshold limits and untested
accessibility/OS motion/variation. No new completion-duration result is claimed.
A source-check helper initially used the system interpreter, which lacked dotenv;
it was rerun with the existing backend virtual environment, with no installation.
That was a tooling error, not an application failure. Temporary test services/tab
were closed. Final report remains a review draft until student acceptance and a
real published Part 2 checkpoint supplies pinned accessible links. No commit,
push, merge, visibility change, upload or submission.

See [final review](../docs/assignment3-part2-readiness.md),
[checkpoint/submission checklist](../docs/assignment3-part2-submission-checklist.md)
and [final review evidence](assignment3-part2-final-review/review-verification.json).

## Authorized Part 2 checkpoint checks — October 27, 2026

Student approved the final report/limitations and authorized reviewed checkpoint
commit/publication on codex/assignment3-part2-foundations. Full mocked backend
suite passed 492 tests (two existing deprecation warnings); frontend passed 85,
non-fixing oxlint/ESLint and the 53-module production build. TravelView differs
from the previous travel App.vue only in adjusted relative import paths.
The actual live flag remains disabled; ledger remains 4/$0.40 reserved, 6/$0.60
remaining. No extra live call, dependency change, merge, visibility change or
Canvas submission. Publication/SHA confirmation is supplied separately after
creating the checkpoint; this source log does not fabricate its own commit.
