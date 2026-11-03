# AI-use disclosure

## Assignment 3 Part 2 continuation — October 21, 2026

Codex reviewed the approved design and implemented the first isolated timing
and reply-rendering foundations with unit tests and documentation. Continued
tools: workspace reads/edits and local test/lint/build commands. The last
student-reported model label in this chat is GPT-6.1 Sol with medium reasoning
effort (October 12); the model/app version has not been independently rechecked
for this continuation. New skills replies are explicitly mocked; no live model
API, clinical dataset, helpline contact, or sub-agent is used in this step.
See [Part 2 progress](docs/assignment3-part2-verification.md) for scope and limits.

Part 2 session-storage continuation: Codex added isolated SQLite schema/storage,
FastAPI session/history endpoints, temporary-database lifecycle/concurrency/failure
tests, and API documentation. No new provider tool or live model call is used;
the prior model-identification limitation above still applies. Evidence and
verification distinguish API persistence from unobserved browser timing.

Part 2 Vue continuation (October 22, 2026): Codex implemented the separate Vue
experience, retryable journal, API client, history and recovery UI, locally bundled
crisis panel, reduced-motion handling, tests, and documentation. CUA browser
control exercised fictional sessions, one full timed run, outage/restart,
refresh/reconciliation, responsive controls, and travel searches. The helpline
lookup and official Get Help page reverified contacts without contacting services.
A history row/detail inconsistency was observed and corrected. The drafting model
remains student-reported GPT-6.1 Sol with medium effort; runtime identification
was not independently rechecked. No sub-agent, live app model call, new dependency,
real distress disclosure, commit, or publication was used. Screenshots and
curated fictional records are in evidence/assignment3-part2-ui/; limits are in
docs/assignment3-part2-browser-verification.md.

Part 2 mocked-conversation continuation (October 26, 2026): Codex implemented
mock-only routes/storage/migration, optional Vue conversation/history, retry and
late-response handling, tests, and documentation. Browser control tested fictional
before/after messages, deliberately malformed/delayed local fixtures, failure
access, restored history after restart, and travel searches. Local helpline lookup
rechecked listed contacts; no crisis service or live app model was called. The
full regression suite exposed a SQLite cross-worker connection bug, which was
corrected and tested. Existing cloud-managed dependencies stalled reads; the
student redownloaded them. Uvicorn protocol reads still timed out; browser QA used
a temporary HTTP/TestClient bridge to the same FastAPI app. No installation,
sub-agent, commit, push, or upload occurred. Student-reported GPT-6.1 Sol/medium
remains the disclosure identifier; runtime model/app version was not independently
verified. See docs/assignment3-part2-conversations.md and curated evidence.

Part 2 display-preference continuation (October 26, 2026): Codex implemented
explicit saved display choices, optional setup reuse, reset, schema v3 migrations,
strict API/revision checks, and backend/frontend tests. CUA exercised the normal
Vue/Uvicorn application with fictional setup/session data, including reload,
backend outage/restart, local/remote reset, crisis access, and travel searches.
The normal Uvicorn startup limitation from the preceding step was resolved. The
reloader scope was narrowed after actual dependency-download changes caused
repeated reloads. A stale reset-progress notice was observed, fixed and retested.
No dependency was installed/upgraded, no app model call or crisis contact was
made, and no sub-agent, commit, push or upload was used. The local helpline lookup
matched the existing bundled contacts. Student-reported GPT-6.1 Sol/medium and
unverified desktop/runtime identification remain unchanged. See the preference
verification guide and curated evidence for current scope and limits.

Part 2 history-clear continuation (October 26, 2026): Codex implemented confirmed
clearing, schema v4/history-generation checks, pinned frontend writes, retry and
late-response guards, tests and documentation. All deletion checks used temporary
SQLite files; browser automation clicked confirmation only against disposable
fictional QA data. It checked cancellation, crisis/leave, clear success, failed
status loading, new post-clear conversation, reload/restart and travel behavior.
Development databases were hashed, not exported, and stayed unchanged. A broad
browser selector was corrected to target the active dialog; a stale post-reload
selector was re-inspected. Frontend check commands initially ran in the root and
were corrected to frontend/. No app model/provider call, dependency install,
sub-agent, crisis contact, commit, push or upload was used. The local resource
lookup matched bundled contacts. Student-reported GPT-6.1 Sol/medium and the
runtime/app-version identification limits remain as previously disclosed.

Part 2 readiness review (October 26, 2026): Codex reviewed the full supplied
assignment, approved design, working code and prior evidence; reran existing
checks; used CUA with temporary mock-only Uvicorn databases and the production
preview to verify the integrated flow; and drafted the separate Part 2 report
and readiness matrix. The report explicitly identifies the missing real model
contribution and uncommitted/unpublished version. A first run lost DOM timing
after a page reload; a production-preview repeat captured 60.011 s and the
original run remains clock-only evidence. The review created documentation and
curated screenshots/JSON only; no app/dependency change, live provider call,
sub-agent, crisis contact, commit, push or submission occurred. The student-
reported drafting identifier remains GPT-6.1 Sol/medium, not independently
verified runtime identification. No Assignment 3 recording or live-model result
was invented; earlier hotel calls are not skills-model evidence.

## Assignment 3.1 disclosure (preserved)

Status: Assignment 3.1 disclosure, updated October 12, 2026. The student reported
the drafting model as **GPT-6.1 Sol**, with **medium** reasoning effort. Desktop
app version is unavailable in this record; add it if readily visible, otherwise
retain that limitation rather than inventing a version.
This disclosure covers the documented Assignment 3.1 design work; it does not
claim to be a complete retrospective inventory of Assignments 1 and 2.

## Tools and roles

| Tool | Identifier/version | Role in this milestone |
| --- | --- | --- |
| OpenAI Codex desktop assistant | GPT-6.1 Sol, medium reasoning effort (student-reported October 12, 2026); desktop app version unavailable. | Read the assignment and repository; propose scope, experience flow, technical records, model boundaries, research mappings, and documentation; check documentation and existing regression checks. |
| Assistant workspace tools | exec_command and apply_patch; exact tool version unavailable. | Read existing source files, write Markdown documentation, and run verification without installing dependencies. |
| Assistant web tool | web.run; exact tool version unavailable. | Inspect official resource pages and record source-verification limits. |
| Local helpline lookup | hotline.get_local_hotline; exact tool version unavailable. | Retrieve listed U.S. helpline contacts for proposed resource documentation. No call, text, or service chat was initiated. |

No image generator, AI-created raster asset, external clinical dataset, or
sub-agent was used for this milestone. The Mermaid flow and text sketch are
assistant-generated design artifacts. No skills-app provider call was made.
Assistant drafting itself is AI use; it is separate from the app's live model
integration, which does not exist yet.

The student supplied the assignment and complete research table, chose paced
breathing and optional before/after conversation, and confirmed same-repository
organization, a separate database, U.S. resource scope, and constrained replies.
The assistant proposed designs and tradeoffs; student review and final
submission decisions remain the student's responsibility.

## Existing provider configuration is not milestone use

The repository contains pre-existing OpenAI/OpenRouter clients and configured
model names from earlier hotel work. Reading those files does not establish
which model generated this chat or imply those models were called for Part 1.
Do not substitute an app backend default for the Codex drafting model identifier.
Earlier assignment tools/models and live runs are described in their existing
documentation and should be disclosed separately if a cumulative report is
required by the instructor.

## Review and unresolved items

- Drafting model/effort is recorded from the student's report; add desktop version
  if available. Unavailable tool versions are explicitly labeled above.
- Review the generated documents against the assignment before accepting them.
- Keep code reuse claims marked as planned until actual implementation occurs.
- Maintain this disclosure when tools/models change in later milestones.
- Record measured testing, failures, and live calls separately from proposed
  checks. See the [curated log](evidence/assignment3-part1-log.md).

## Assignment 3 Part 2 — disabled skills adapter follow-up

The student selected OpenAI `gpt-6-luna`, a maximum of ten skills dispatches and
$1 total, and explicitly prohibited live calls during implementation. Codex
implemented a disabled-by-default adapter, versioned selection instructions,
schema-v5 migration, durable pending/cancelled runs, clear-generation-safe final
writes, a nonrefundable reservation ledger, bounded HTTP/response handling, and
composer disclosure/cancellation changes. Official OpenAI model, structured-output
and pricing pages were read; the existing backend-only key's presence had been
checked without printing it or calling a provider. The actual .env was unchanged.

All provider requests during verification used injected MockTransport with fake
credentials and temporary databases. A separate mock-only browser harness used
temporary skills/travel files and blocked provider access. The initial checks
exposed old v4 fixture assumptions and an overly strict query-parameter type;
fixtures and the status query contract were corrected and checks rerun. The
curated adapter guide/evidence documents actual results and unverified items.
No real model selection result, actual billing, provider-resolved snapshot,
clinical benefit, live authorization, checkpoint or submission is claimed.
The student-reported Codex setting remains GPT-6.1 Sol, medium effort; this is
separate from the chosen application API model, not independent UI verification.

## Assignment 3 Part 2 — explicitly authorized four-case live check

The student subsequently authorized up to four fictional OpenAI gpt-6-luna checks,
reverification of pricing/remaining durable allowance, counting failures, no
retries, temporary live mode and restoration to mocks. Official pricing was
reopened and the existing skills ledger inspected/migrated to v5 with no reset:
zero reservations and all ten/$1 available. A single-use local harness called
the actual FastAPI route and real HTTPS provider, captured only safe model/status/
usage metadata, and preserved application rendering/storage enforcement.

All four attempts returned HTTP 200/completed with expected reviewed selections:
typing, static motion option, supported-scope boundary and fictional support
signpost. The unsupported request reused the typing conversation's history. The
motion example used after placement without an associated completed session.
Provider returned gpt-6-luna on all four, not a distinct dated snapshot. Actual
billing was not inspected. Four nonrefundable $0.10 reservations leave six calls/
$0.60, not a claim that $0.40 was billed. No failures, retries or fifth probe.

Mock mode was restored in a finally block and independently checked; .env,
travel data and saved preferences were unchanged. SQLite and history restored
four live runs/eight messages across three conversations. Full mock regressions
passed (492 backend, 85 frontend, lint/build). App source was unchanged. The
curated batch/verification records contain fictional messages and application-
rendered replies, not credentials, raw provider prose/reasoning or raw errors.
Nothing was committed, pushed or submitted. These four one-off cases are not a
clinical assessment, full live UI verification or the Part 3 evaluation.

## Assignment 3 Part 2 — final readiness review, October 27, 2026

At the student's request, Codex compared the full assignment and approved design
against existing implementation/evidence, finalized the Part 2 review draft and
created the checkpoint/evidence/manual-submission checklist. No application source,
dependency, live setting, original skills data, commit or publication was changed.
No additional provider call was made: the ledger remains four reservations/$0.40,
leaving six/$0.60 of conservative allowance.

A temporary mock-only actual-app/production-preview browser check confirmed the
simpler-view difference, invalid-selection fallback, support pausing/staying
paused, explicit Resume/Stop and genuine backend-outage draft/support/Leave.
A separate read-only server blocked every non-GET request and all providers while
showing actual saved live replies in history. Its original database hash remained
unchanged. Temporary mock data and curated screenshots contain fictional cases.
Only review-created test services/tab were stopped. The last 492-backend/85-frontend
lint/build gate was not rerun merely for unchanged-source documentation; its skills
fingerprint was rechecked. The review discloses simpler-view contraction, missing
exact run-status badges despite copy, timing/setup and accessibility/variation
limits. Student approval, actual Part 2 commit/pinned links and grader access remain
pending. No Canvas action was performed.

## Assignment 3 Part 2 — authorized checkpoint preparation, October 27, 2026

The student approved the final report and disclosed limits and explicitly
authorized mock-only checks, a reviewed Part 2 commit and branch publication.
Codex reran the full mocked gates: 492 backend tests, 85 frontend tests, non-fixing
linters and production build passed. It reviewed the travel extraction (import
paths only), scoped the reviewed source/docs/evidence, checked local links and
excluded actual .env files, databases, dependencies/builds and credentials. No
new live provider call occurred; the original ledger stays four reservations/
$0.40, with six/$0.60 remaining and mode mock. Exact commit and verified remote
links belong in the separate upload-ready report produced after publication.
No merge, visibility change or Canvas action is authorized or claimed here.

## Assignment 3 Part 3 — first refinement/evaluation scaffold, November 2, 2026

The student requested beginning Part 3 after confirming the full assignment was
available. Codex read the approved design and Part 2 review, created the separate
codex/assignment3-part3-refinements branch from the published checkpoint, and
preserved the existing untracked submission artifacts and prior reports.
It implemented a tested conversation-entry visibility policy for Simpler view
and corrected live cancellation copy to match message-based history. It retained
compact ready-screen display controls and documented the D1/D3 versus D5/R4
tradeoff instead of claiming all optional choices were removed.

Verification used the existing backend/frontend tools: 492 backend tests, 87
frontend tests, non-fixing oxlint/ESLint and production build passed. Browser
checks ran through computer-use tools against the actual app/production preview,
temporary databases, absent keys and a forbidden provider transport. Saving the
simpler setup and support/Back/Stop were observed. Original database/earlier-report
hashes were unchanged. Native screenshots capture a cropped portion of the DOM
viewport; they are not a full accessibility/mobile-edge proof. Live-composer copy
was source/compile reviewed rather than enabling live mode for a screenshot.

The helpline lookup reconfirmed the same U.S. contacts; no service was contacted.
No live model call, dependency installation, commit, push or submission occurred.
The existing ten-call/$1 ledger remains four/$0.40 reserved, six/$0.60 remaining.
The new Part 3 plan, 15-row matrix/three behavior checks and report scaffold mark
formal observations, repeated live evaluation, new timing, clean checkout and
recordings as pending/partial rather than fabricating them. A Part 2 video was
not confirmed or relabeled as a completed Part 3 recording. Existing tool/model
identity disclosures remain; no new provider model result is claimed.

## Assignment 3 Part 3 — full mock evaluation, November 2, 2026

The student explicitly requested the fifteen scenarios/B1–B3, fresh complete
exercise/setup measurement, failure/personalization/history checks, preservation
of original databases/ledger and no real calls/install/commit/push/submission.
Codex saved expected outcomes and a source fingerprint before execution, then
used computer-use tools with the actual app/production preview, temporary DBs,
no credentials and forbidden provider access. All fifteen planned scenarios passed
under the documented conditions. Source code was unchanged during this evaluation.

Observed DOM telemetry was 60005 active ms, 60002 clock ms, 17146 setup ms, twelve
ordered cues/six cycles, no pause/support/chat inside the fresh run. These are
actual displayed/app-instrumented values, not hardware-paint or phase-jitter
proof. Reduced motion used a declared JavaScript matchMedia fixture; actual OS
settings and full CSS/media integration were not changed/tested. Reset failure
used a named temporary SQLite trigger and explicit user Retry; the actual
preference controller also ran with injected local promises for an in-flight save.
Two S15 synthetic dispatches used actual ASGI routes, a fake key and MockTransport
in another temp DB; its schema's live-mode label is not actual provider evidence.

Backend shutdown/restart/outage were real local test-service actions. Clear Cancel
preserved data; confirmation removed only backed-up temporary history and kept
preferences/ledger. Old writes failed; new-epoch activity saved. A delayed mock
still saving after Leave was documented as a counterintuitive best-effort result;
late UI guards worked. No paid failure or clinical finding was fabricated.
The initial backend helper invocation lacked the repo module path; correcting
PYTHONPATH ran it successfully without installing a package or changing app code.

Full mocked regressions passed 492 backend / 87 frontend tests, non-fixing lint
and build; two existing backend deprecation warnings remain. Original DB/prior-
report hashes match before/after; original ledger is still four/$0.40 reserved,
six/$0.60 left. No real model calls, installations, commits, pushes or submissions.
Only test services/tab were closed. Evidence and the matrix/report distinguish
observations/simulations from pending live repeats, clean checkout and recordings.


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


## Authorized Part 3 checkpoint — November 3, 2026

Student approved report/limitations and authorized commit, exact fresh-checkout
verification with declared dependencies only, conditional origin publication and
a separate pinned upload report. Precommit mocks passed492 backend/87 frontend,
nonfixing lint/Vite8.2.4 build against matching isolated source/tests/lock. Scoped
Part3 paths exclude original data/credentials/environments/videos/prior submission
outputs. Configured credential values scanned without printing them; helper used
the existing backend interpreter after system Python lacked dotenv. Seven
moderate findings remain unresolved. Post-commit setup/publication outcomes will
be recorded in separate submission metadata; no future result is asserted here.
No live call, merge, visibility change or Canvas submission authorized/performed.
