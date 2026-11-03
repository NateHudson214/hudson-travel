# Assignment 3 Part 3 — Curated process evidence

## Step 1 — refinement and evaluation setup, November 2, 2026

User prompt: “Lets begin work on part 3 of assignment 3 then!” The full assignment
and approved notes were already available. Began on separate branch
codex/assignment3-part3-refinements from published Part 2 checkpoint
16deb696c24222519c88be73f6d29df1a3fbab76, preserving untracked submission output.
No old recording, submission or new model output was assumed.

Part 2 evidence showed optional conversation remained in simpler ready/stopped
views. The first refinement added a presentation policy used by the actual Vue
entry and tested for ready/completed/stopped versus running/paused/history.
The browser now hides it in simpler ready/stopped views and restores it through
Show more without starting/restarting breathing. Cancellation copy now directs
to saved messages rather than run-status badges absent from the history UI.

Reviewed alternative: hiding the entire preference panel whenever simpler=true
would also hide the action needed to save that setup. The implemented choice
retains compact ready-screen Save/Use last setup/Reset, while reducing conversation/
history/explanations. This is a documented revised design decision, not a failed
runtime test, new patient finding or claim of optimal emotional cost. A surprising
formal evaluation result remains pending and must come from observed evidence.

Full regression results: 492 backend tests, 87 frontend tests, both non-fixing
linters and a 53-module build passed; two existing backend deprecation warnings.
Fresh contact lookup returned the same bundled U.S. resources; the prior displayed
resource version/date and URLs were not changed and no service was contacted.

Browser checks used actual app/Vite preview with temporary skills/travel DBs,
no credentials and forbidden provider dispatch. Ready/stopped visibility,
Show more, explicit simpler-save retaining ready state, and support/Back/Stop
passed. Completed visibility was unit-tested only; no fresh completed-browser or
exercise duration is claimed here. Live-only wording was source/compile reviewed.
Safety/Leave DOM rectangles fit a 1280-pixel viewport; the native screenshot
captures only part of it, so cropped images are not full viewport/mobile proof.

Both original databases and prior report hashes remained unchanged. Original
ledger is four reserved calls/$0.40; six/$0.60 remain. Temporary model runs and
reservations are zero. Only this step's QA services/tab were stopped. No dependency
installation, live model call, commit, push or submission. The full 15-scenario
matrix/three behavior checks, repeat-live authorization, clean checkout, final
recordings/code explanation and final report/checkpoint remain unfinished.

Evidence: [step verification](assignment3-part3-step1/verification.json),
[simpler ready](assignment3-part3-step1/simpler-ready.jpg),
[saved simpler setup still ready](assignment3-part3-step1/saved-simpler-ready.jpg).
Plan: [Part 3 work](../docs/assignment3-part3-plan.md) and
[evaluation matrix](../docs/assignment3-part3-evaluation.md).

## Step 2 — full fifteen-scenario mock evaluation, November 2, 2026

Student explicitly authorized full mock/browser/temp-database evaluation and
prohibited real calls, installation, commit, push and submission. Saved expected
outcomes and app-source hashes before observing results. The same production
build/actual app ran against named temporary skills/travel databases; keys were
absent and the real provider transport forbidden.

All S01–S15 passed under the documented conditions, with B1 independent safety/
exit, B2 application/user authority and B3 durable generation/idempotency/allowance
checks. Fresh S03: 60005 ms DOM active, 60002 clock, 17146 setup, twelve ordered
cues/six cycles, zero pauses/support and no conversation request within pacing.
This is one visible-browser/static-cue sample, not hardware paint or jitter proof.

S04 pause froze active=8267 ms and the same exhale remainder; final record separates
8834 active / 17118 other-pause / 10233 support ms. Support from both paused and
running returned paused. S06 active/pending Leave was immediate, while its delayed
local mock later saved a completed pair. The late UI response stayed ignored.
Decision: keep accurate best-effort cancellation wording and UI generation guards;
do not promise server undo. This observed counterintuitive outcome is consistent
with the contract, not an invented new clinical or paid-provider failure.

Named malformed fixtures/contract variants returned fallback and stored no raw
unapproved text. S11 saved/reloaded/reused choices explicitly; a test-only JS
matchMedia fixture forced a static cue over saved gentle motion. No actual OS
change/full CSS emulation is claimed. S12 temporary SQLite-trigger failure left
local reset usable with warning; explicit same-request retry succeeded after the
trigger was removed. A local-promise test verified reset waits behind an old save
and uses fresh revision 1; history stayed intact.

S14 genuinely stopped/restarted the test backend. A 283 ms acknowledged paused
checkpoint restored without resuming; explicit interruption preserved the same
lower-bound duration. Completed session and conversation history restored with
no new model run. S10 actual backend outage retained an unsent draft/error; local
support and Leave worked, no Retry was clicked, and the unsent draft was absent
from SQLite before history clear.

S13 Cancel preserved five sessions/three conversations. A recoverable fixture
backup and curated records were taken before Confirm removed only temporary
history (33 events/eight messages/four runs), kept saved display choices/ledger
and advanced epoch to 1. Old writes returned 409. A later valid epoch-1 mock turn
saved as new history, not resurrection. S15 actual routes plus local MockTransport
verified duplicates do not redispatch, cancellation stays cancelled, and a clear
rejects late final saves/retries while preserving preferences and two nonrefunded
fake reservations. These are two synthetic transport calls, zero real provider calls.
The first helper launch needed PYTHONPATH corrected; no package was installed.

Final gates passed: 492 backend tests, 87 frontend tests, both non-fixing linters,
53-module build; two existing dependency warnings. Original DB/prior-report hashes
and app-source fingerprints match. Original ledger remains 4/$0.40 reserved,
6/$0.60 remaining. Only the test services/tab were closed. Live repeats, clean-
checkout verification, final recordings/code explanation and checkpoint remain
pending. No real call, install, commit, push or submission occurred.

Evidence: [expected](assignment3-part3-evaluation/expected.json),
[results](assignment3-part3-evaluation/results.json),
[browser observations](assignment3-part3-evaluation/browser-observations.json),
[timing](assignment3-part3-evaluation/timing.json),
[records before temporary clear](assignment3-part3-evaluation/records-before-clear.json),
[reset race](assignment3-part3-evaluation/preference-race.json),
[pending races](assignment3-part3-evaluation/backend-races.json),
[full matrix/method](../docs/assignment3-part3-evaluation.md).


## Part 3 repeated live batch — November 2, 2026

Student authorized at most four fictional OpenAI gpt-6-luna dispatches, no retries,
current pricing/remaining original allowance checks and restoration to mock.
Used OpenAI Docs skill; opened current official model/pricing pages before calls.
Read-only preflight confirmed four previous reservations, six available and no
pending run. Corrected the harness preflight .env path before any dispatch;
corrected a read-only verification table name. Neither caused a paid retry.

Actual app ASGI route/production adapter and observed real HTTPS transport sent
four attempts in independent conversations: typing timeout/expected selection,
then two identical expected motion selections. The timeout counts, no fifth
attempt, and no response selection/usage is invented for it. Successful provider
responses reported gpt-6-luna; context hashes match within each pair. No raw
provider prose/reasoning/errors or credential was stored. Exclusive journal
prevents accidental rerun. Mock mode restored in finally; .env unchanged.

Original ledger now eight/$0.80 reserved, two/$0.20 remaining. Existing records,
preferences/epoch, travel database, source and prior reports preserved; four new
conversations/eight messages and one failed/three completed runs persist. No
pending run; integrity/foreign keys valid. History reads made no provider call.
164 mock skills backend tests passed with two existing warnings. No installation,
application change, commit, push, server or submission. No live browser Send.
Report records the genuine finite-timeout availability tradeoff and insufficient
successful typing samples; no broad reliability/clinical or billed-cost claim.

See docs/assignment3-part3-live-checks.md and
 evidence/assignment3-part3-live-checks/{batch,verification}.json. Clean-checkout
verification, final recordings/code explanation and checkpoint remain pending.


## Part 3 isolated fresh setup — November 2, 2026

Student authorized declared-dependency installation only inside an isolated current-
files copy, temporary DBs/mocks, preservation and no live/commit/push/submission.
Copied 235 source/docs/evidence files without .git, secrets, DBs, dependencies or
separate submission outputs. New venv and npm dependencies installed after initial
restricted DNS attempts were rerun with network permission. No declarations/lock
or application source changed. Python requirements resolved pytest 9.2.0 and newer
framework versions; versions recorded, not silently matched to old environment.

Full gate: backend 362 passed/130 setup errors; frontend 87 passed, nonfixing
linters/build passed. Isolated reproduction: pytest MonkeyPatch undo deletes a
dynamically stored Starlette State setting, breaking later fixtures. Plugin-
disabled conversation diagnostic still 2 passed/23 errors. No test-tool patch or
pin applied. npm installer reported 11 advisories (7 moderate/3 high/1 critical),
untriaged; no audit fix. This is a partial pass/blocker, not completed clean checkout.

README reload/dev startup worked after local-port permission; actual endpoints
and browser verified travel six search cases, mock reply persistence and breathing
Start/Pause/Stop/support paused return. No new full-duration run. A first browser
snapshot preceded results; explicit visible-result waits/rechecks passed. A version-
list helper initially used the wrong folder, then succeeded from the copy root.
No app repair was made. Only test tab/processes closed; original protected hashes
and ledger preserved at eight/$0.80 reserved/two/$0.20 remaining. Temp ledger zero.
See docs/assignment3-part3-setup.md and evidence/assignment3-part3-setup/. Next is
focused compatibility repair/advisory triage and repeated isolated verification;
committed checkout, recordings and publication remain pending.


## Part 3 fixture repair and npm advisory triage — November 2, 2026

Student authorized test compatibility repair without version changes and read-only
advisory triage, no installations/live/commit/push/submission. Replaced 29 dynamic
State attribute patches across five skills test files with dictionary item patches.
First pass missed one multiline clock-provider call: 444 passed/48 errors; corrected
it and retained the failure evidence. Final isolated full backend 492 passed with
existing pytest 9.2.0. Original-env skills 164 passed/two existing warnings. Separate
isolated in-process 164 passed/all original State keys/bindings restored; one
harness assertion-rewrite warning. No source/library/version workaround or skipped
tests. Production/UI unchanged, so prior frontend/browser checks were not repeated.

Read-only npm audit and primary GitHub advisories plus installed paths confirmed
11 flagged packages (7 moderate/3 high/1 critical); five carry twelve direct
advisories and six inherit the ESLint chain. Input-path risk judgments labeled
inferences; no exploit or universal safety claim. Proposed compatible Vite 8.2.4,
shell-quote 1.11.0, source-map-js 1.2.2, brace-expansion 5.0.12 await approval.
Patched minimatch 11.0.1 conflicts with current ^10 parent ranges; latest metadata
still ^10. No forced override/ancient automatic downgrade. All findings remain
installed; no student risk acceptance inferred. No packages installed or updated.

Original protected hashes/allowance unchanged (8/$0.80 reserved, 2/$0.20 remain);
application source/dependency/lockfiles unchanged. Updated setup guide, plan, report,
README and evidence, retaining initial historical failures. Snapshot plus corrected
tests is unpublished, not committed clean checkout. See
 docs/assignment3-part3-compatibility.md and evidence/assignment3-part3-compatibility/.
Next: student decision on compatible dependency updates and separate lint-chain
remediation, then final readiness/media/committed-checkout work.


## Part 3 approved dependency updates — November 2, 2026

Student authorized four exact versions in the isolated copy, copying the lock back
only after verification and read-only remaining lint-chain investigation. Used npm
lock-only resolution with temporary exact constraints, restored original package
JSON, normalized, then npm ci --ignore-scripts only in the existing isolated copy.
Exactly four package records changed: Vite 8.2.4, shell-quote 1.11.0, source-map-js
1.2.2, brace-expansion 5.0.12. No final direct additions/overrides/major upgrade.
Verified 492 backend/87 frontend, nonfixing lint, Vite 8.2.4 build and browser travel
six searches/simpler choices/mock save/exercise controls/paused support return.
A DOM checkbox locator mismatch resolved using fresh AX/indexed control; no app
repair or inferred defect. No new complete-duration run. Copied verified lock only
after gate; original frontend node_modules was not reinstalled.

Audit now seven moderate/no high/critical, same lint-chain residual. Official
advisory and registry checked; no patched minimatch 10 found; latest parents still
^10. Installed lint paths default optimization level 1 versus reported >=2 trigger.
Lower observed exposure is an inference, not a patched package or blanket safety
claim. No exploit, forced downgrade/override or major change. Remaining limitation
not accepted by student. Read-only npm metadata and audit are not model calls.

Original protected hashes and ledger preserved (8/$0.80 reserved, 2/$0.20 remain),
mock/key-free temporary DBs have zero reservations and mock-only saved turns.
Only test servers/tab closed. No live call/commit/push/submission. Current snapshot
is unpublished, not committed clean checkout. See docs/assignment3-part3-dependencies.md
and evidence/assignment3-part3-dependencies/. Final readiness decisions, recordings,
code explanation and eventual committed verification/publication remain pending.


## Part 3 final readiness review and silent recording scripts — November 2, 2026

Reviewed the original full student-supplied assignment and R/D table against
source and curated evidence. Read-only consistency checks confirmed all15 cases,
B1-B3, actual 60.005/60.002 seconds plus17.146 setup, real four-attempt batch
(3 expected/1timeout), repaired tests, exact locked dependency graph and original
protected hashes/ledger. No regression suite was rerun or new timing fabricated;
latest 492/87/lint/Vite8.2.4 gate applies to matching source/tests/lock.

Prepared two exact silent recording scripts and sixteen caption cards, including
an uninterrupted complete exercise, optional mock conversations, display reuse/
reset/history, independent support/exit, real historical failure/revision evidence
and generated-code explanation. Source inspection corrected the after-conversation
Back label in the script. Browser tool blocked local file-protocol card preview;
no workaround attempted. Static syntax/link checks do not establish visual/media
quality; manual review remains pending. No app service was started for this review.

Rewrote the Part3 draft around final behavior/evidence/limits; no actual video,
URL, submitted commit or instructor access invented. Seven moderate lint-tool
findings stay unresolved, without implied risk acceptance or upgrade permission.
Readiness matrix separates verified copied-files setup from outstanding committed
checkout, actual media/code explanation, final decisions, checkpoint/pinned links
and grader/Canvas checks. Prior reports/data/allowance preserved; no installation,
provider call, commit, push, upload or submission. Model disclosure remains the
student-reported GPT-6.1 Sol medium with runtime-version caveat; actual API model
identifiers/mocks are distinct. No subagents used.


## Demo A review and B preparation — November 3, 2026

Student reported finishing A and requested review/B preparation. Located the new
Desktop MOV (its name changed from assigment3 to assignment3 while locating it).
Built-in macOS AVFoundation reader initially failed against the old path, then
restricted video decoding failed; the approved unrestricted reader extracted
metadata/32 ten-second sample frames plus last frame. No install, video edit or
upload. Sampled review found 307.345 seconds, 2866x1494, no audio; selected original-
resolution frames show timing60.02 rendered/60.01 clock/56.26 setup. Main sequence,
mock/history/reuse/reset/support/Leave seen. Fixed bottom Pause/Resume/Stop bar is
outside the capture. This is a recorded-region gap, not a missing app control.
No continuous-playback, all-frames/privacy or brief-clear-dialog certification.

Preserved original video; saved its hash, metadata, two review frames and limits.
Prepared a13-page local single-file B walkthrough embedding actual curated error,
reproduction, correction/passing result and generated timing/reply/deadline code
excerpts with provenance. Generator initially requested nonexistent provider line104;
corrected to actual103, static syntax passed. No source evidence/application code
was changed. Browser local-file preview was already policy-blocked; did not retry
or circumvent. Manual visual preview still required. Updated B script with a short
full-viewport control supplement, silent recording instructions and hold times.
B not recorded, hosted or approved; seven moderate lint findings remain unresolved.
No paid provider request, dependency install, commit, push or submission.


## Both-recording review — November 3, 2026

Student reported B saved and explicitly accepted A framing as-is. Read actual
Desktop MOVs without modifying them. macOS decoder produced B metadata and22
samples at10-second intervals/last second; inspected contact sheets and selected
full-resolution error/code/closing frames. B is202.530s,2866x1494,no audio. All13
walkthrough sections observed: actual historical failure/evidence/revision/result,
generated pacing/support/reply/deadline code and live timeout/unresolved limits.
A hash still matches its32-frame sampled review (307.345s,silent). No continuous
playback/all-frame privacy certification. No retake/supplement required for A.
B's prepared intro mentions a preceding supplement absent from the recording;
this is not claimed as captured evidence. Intro/tail cleanup is optional; recording
controls appear near the end. No media edits or uploads. Original movies remain
on Desktop, not added toGit; curated hashes/metadata and two B stills added.

Updated report/readiness/README from scripts-only to actual sampled local media,
keeping final playback/hosting, seven unresolved lint findings, committed checkout,
final report approval, published SHA/pinned evidence and grader/Canvas steps open.
A-framing acceptance does not imply dependency risk acceptance or commit permission.
No new tests, installations, provider calls, commits, pushes, uploads or submissions.


## Hosted recording links — November 3, 2026

Student supplied OneDrive/SharePoint links for demo A and process B. No connected
OneDrive reader was available, so CUA opened the exact supplied URLs read-only;
both redirected to Penn State Microsoft sign-in. No login credentials entered,
SSO redirect tokens retained in evidence, permissions changed or files uploaded.
Student then explicitly confirmed instructor/applicable graders can view both.
Recorded this as student-attested permission, distinct from agent-hosted playback
or byte matching, neither independently verified. Exact supplied links added to
Part3 report and curated hosted-links.json; temporary sign-in tabs closed.

Kept A framing acceptance and seven unresolved lint findings distinct. Final
hosted playback, report/checkpoint approval, committed clean checkout, published
SHA/pinned evidence and repository grader access/Canvas remain. Original data/
allowance preserved, mock mode unchanged; no install/model call/commit/push/
upload/submission. No institution-private login trace copied into repository.


## Authorized precommit gate — November 3, 2026

Student authorized the Part3 checkpoint and conditional publication. Fresh mock
gate passed492 backend/87 frontend, nonfixing lint and Vite8.2.4 build using matching
isolated inputs. Protected original hashes/ledger and disabled mode preserved.
Scoped reviewed files only; no videos/DBs/credentials/environments/submission
outputs. See assignment3-part3-checkpoint/precommit.json and gate logs. Actual
resulting commit/fresh-checkout/publication checks are separate post-commit facts,
not fabricated in this precommit record. No live call/merge/visibility/Canvas.
