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
