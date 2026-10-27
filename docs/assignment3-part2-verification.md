# Assignment 3 Part 2 — Implementation progress

Updated: October 26, 2026. Foundations, sessions, Vue view, mocked conversation, display preferences, and confirmed history clearing.
This does not mark Assignment 3 Part 2 complete.

## Scope and acceptance

Reviewed AGENTS.md, README, Part 1 plan/experience/technical/resource notes, and
the current test configuration. The published Part 1 checkpoint was clean at
the start. Work is on codex/assignment3-part2-foundations; no implementation
commit or push is requested for this step.

Acceptance for the first step: six fixed four-second inhale/six-second exhale
cycles; monotonic elapsed-time accounting; distinct setup, active, user-pause,
and support time; explicit resume/stop; delayed callbacks cannot silently skip
cues; mocked responses render only reviewed reply/fact IDs with no arbitrary
prose or timer commands. Existing travel checks must continue to pass.

## Implemented

- frontend/src/skills/breathing.js: isolated, injected-clock session engine and
  immutable schedule/snapshots. The caller must explicitly start, tick, pause
  when hidden, and invoke support controls; DOM/listener integration is not
  implemented. Terminal sessions do not restart; create a new engine to restart.
- backend/app/skills/replies.py: versioned catalog, compatibility allowlists,
  strict object validation, and an explicitly injected local mock reply helper.
  Invalid input does not call a mock. A failed/malformed mock has no retry and
  returns fixed text that mentions the planned independent support control.
  That text does not imply the control already exists in a running interface.
- Test discovery includes frontend/src/skills/*.test.js alongside existing API
  tests. No dependency declarations/lockfiles changed.

The approved catalog lives in Python for this first step, exposed as a fresh
context dictionary. This replaces the proposed separate context.json for now
to keep validation and rendering definitions together. There is no provider
request, prompt file, or network client in the new skills modules. A future
provider adapter must use this boundary rather than render free-form output.

## Timing decision and limits

The engine advances from sampled monotonic elapsed time, not interval counts.
On a callback more than 250 ms past the pending phase deadline, it pauses with
reason timing and retains the last sampled phase/remaining time rather than
skipping a cue. The delay still counts toward active duration. This **provisional
software threshold** makes interruptions testable; it is not clinically derived
or validated in the target browser. Browser measurements may justify revising it.

Small callback delays are preserved in recorded active duration (for example,
60,100 ms at final completion instead of clamping to 60,000). A simulated
interruption/resume case totaling 95,000 ms is flagged outside the 90-second
limit without forcing departure or claiming it passed. Support time and other
pause time are mutually exclusive. Setup includes time before Start.

An engine tick is not proof a cue was rendered. The UI still needs to align
Start/completion with rendered cues, record actual transitions, connect tab
visibility, clean up scheduled callbacks, and measure browser duration. No
actual 60-second browser exercise, accessibility, or user experience is verified.

## Verification commands

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests/skills -q
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests
```

From frontend/:

```bash
node --test src/skills/*.test.js
npm test
./node_modules/.bin/oxlint .
./node_modules/.bin/eslint . --no-cache
npm run build
```

Results after the student made dependencies available locally:

- Full backend suite: 355 passed, including 27 new skills reply cases; two
  non-failing existing dependency deprecation warnings remain.
- Full frontend suite: 51 passed, including 13 injected-clock skills tests.
- Both frontend linters passed without auto-fix.
- Production build passed: Vite 8.2.2 transformed 28 modules. The sandboxed run
  and an unsandboxed retry both exited successfully after the initial wait.
  Build output reported slow plugin hooks; these were non-failing timing notices.
- git diff --check passed, including a read-only unsandboxed retry after the
  original check waited for repository file reads.

Tests contain only fictional inputs, injected clocks, and local mock outputs.
No live provider call or crisis contact was initiated. The first independent
reply test run found a test assertion issue: a naive sentence counter split the
abbreviation "U.S.". The assertion was corrected to recognize sentence boundaries
followed by a capital letter; all 27 cases then passed. Application behavior was
not changed to accommodate that assertion.

The first verification attempt stalled while reading cloud-only dependency
files. A diagnostic stack showed Python waiting in dependency import file reads;
metadata identified dataless placeholder files. After the student's local
download, the standard backend suite completed normally. A fresh process check
found no earlier task verification processes remaining, so none needed stopping.
No dependency was installed or upgraded, and no unrelated process was stopped.
All commands started for the resumed verification exited; no new verification
process was left running. No application service was started. No source/test
code was changed during the resumed checks; only these verification/evidence
notes were updated. The next implementation step has not begun. The first
foundations step is verified at the unit/regression level and remains uncommitted.

## Remaining Part 2 work

1. Review remaining Part 2 requirements and prepare a truthful milestone report.
   Confirmed history clearing, display preferences, optional reuse, and reset are implemented.
2. Complete remaining assignment checks and prepare a Part 2 report with only
   observed evidence. Live model integration/quality and peer evaluation are not
   established by this mocked step.

## Second step — Isolated session storage and endpoints

The student authorized session/event storage and lifecycle/history endpoints.
Implemented backend/app/skills/sessions.py and routes.py, mounted at /api/skills
from backend/app/main.py. Skills storage initializes lazily in its own file;
there is no change to travel startup, seeding, endpoints, or CSV inputs. No
frontend source or model code is changed in this step. See the
[API guide](assignment3-part2-sessions.md) for exact request/response rules.

Focused tests: 50 session API cases passed. Coverage includes strict validation,
idempotent creation/events, concurrent conflicting and duplicate requests,
pause/support/stop/interruption, explicit recovery without mutating GETs,
pagination with timestamp ties, client-reported completion limits, persistence
across fresh application instances, atomic rollback, locking, database isolation,
foreign/newer/corrupt schema failures, and continued travel availability.

All cases use temporary databases. Tests check that the temporary travel file
hash is unchanged and that only the three skills tables exist in the skills
file. No development database, live provider, or actual crisis contact is used.
These results do not establish browser-rendered timing, UI functionality, or a
full service-process restart.

Final checks for this step passed: 405 backend tests (including 50 new session
API cases), 51 frontend tests, both non-fixing frontend linters, production build
(28 modules), and git diff --check. The same two backend dependency deprecation
warnings remain non-failing. No dependency was installed or upgraded. The only
change to the shared FastAPI entry point mounts the router and supplies separate
skills path/clock defaults; travel startup and handlers are unchanged. The
development skills database was not created by these temporary-database checks.
No service, live model call, commit, or push was performed for this step.

## Third step — Separate Vue experience

Connected the tested engine and session APIs with a serial retryable event queue,
separate hash navigation, a retained travel view, local crisis dialog, history,
explicit refresh recovery, static/reduced-motion cues, and persistent controls.
Visibility pauses breathing; navigation stops it; returning from support requires
explicit Resume. No new dependency, live model adapter, conversation, preference
persistence, or travel behavior change was introduced.

Current regression gate: 405 backend tests passed (two existing deprecation
warnings), 63 frontend tests passed, both linters and production build passed
(42 modules). The twelve added frontend cases cover API contracts/timeouts,
ordered queues/idempotent retries, snapshot mapping, motion preference, and
bundled resource invariants. Browser interactions supplement those tests; no Vue
component-test dependency was installed. See the
[browser verification record](assignment3-part2-browser-verification.md) for
real timing, failures/corrections, screenshots, and unresolved limits. Earlier
sections describe the state at their own milestone, before UI integration.

## Fourth step — Optional mocked conversation and persistence

Connected before/after conversation and on-demand read-only history through the
approved reply/fact renderer, with no live calls. Schema v2 adds conversation,
message and mock-run records through a tested v1 migration; session APIs remain
compatible. Finite local fixtures cannot control pacing, preferences or navigation.
The composer ignores late responses after unmount; sent turns can still save.

Final checks: 430 backend tests, 67 frontend tests, non-fixing oxlint/eslint,
47-module build, and diff/link checks passed. Two existing dependency warnings
remain. A concurrent-request test exposed a SQLite worker-thread close error;
request-owned connections now allow worker handoff, with a deterministic
regression case. The cloud-only dependency stall and ordinary-Uvicorn startup
limit are recorded in the [conversation verification guide](assignment3-part2-conversations.md).
Browser checks used the real FastAPI routes through a temporary HTTP/ASGI bridge,
normal Vue server, fictional data, and no live providers. This remains partial
Part 2 implementation, not final course submission evidence.

## Fifth step — Explicit saved display choices

Implemented optional Save display choices, Use last setup, and Reset display
choices in the ready view. Schema v3 preserves v1/v2 data and adds one revisioned
singleton. Reading/saving never auto-applies choices or starts breathing; explicit
reuse applies only display settings, with reduced motion retaining precedence.
Reset is local immediately and clears saved choices transactionally without
removing history. Stale writes cannot restore a reset setup.

Final checks passed: 448 backend tests, 74 frontend tests, both non-fixing linters,
50-module production build, diff and local-link checks. Normal Uvicorn/Vite startup
and browser verification passed, resolving the earlier cloud protocol limitation.
The documented reloader now watches only backend/app to avoid reloads from
hydrating dependency files. No dependency installation, live model call, commit,
or push. [Detailed verification/evidence](assignment3-part2-preferences.md) records
outage/reset recovery, persistence, unchanged travel data, a corrected stale
progress notice, and remaining limitations.

## Sixth step — Confirmed clear saved skills history

Added a clear control to both history views, a native confirmation retaining
Crisis support/Leave, atomic schema-v4 clearing, and persistent history generations.
Session/event/conversation writes pin their original generation, so delayed and
retried old requests cannot recreate cleared records. Preference state is retained.
Exact committed-clear retries cannot delete newly created history a second time.

Final gate: 465 backend tests, 81 frontend tests, both non-fixing linters,
53-module build, diff and local-link checks passed. Two existing warnings remain.
All deletion tests, including the successful browser DELETE, used temporary
SQLite databases; development DB hashes were unchanged. Browser checks covered
Cancel, crisis/leave, paused-session discard, success, outage, new activity,
reload/restart persistence, and travel searches. No live calls, dependency
changes, commit, push or submission. [Details/evidence](assignment3-part2-clear-history.md).

## Part 2 readiness review — October 26, 2026

[Readiness matrix and exact remaining sequence](assignment3-part2-readiness.md)
compare the full assignment to the approved design and implementation.
[Part 2 report draft](../assignment3/part2/report.md) is deliberately marked not
submission-ready: actual skills-model contribution and a real published Part 2
checkpoint/access links remain blockers. The Part 3 fifteen-case/live-variation/
recording/clean-checkout requirements are tracked separately.

Reran 465 backend tests, 81 frontend tests, both non-fixing linters and 53-module
build; all passed with two existing backend warnings. A production-preview flow
completed twelve DOM cues in 60.011 s (clock 60.010 s, setup 12.055 s separately).
Before/after mock replies, rejected reply and network failures, pause/resume/
stop/leave, resources offline and SQLite restoration after service restart were
verified. Temporary history generation 2 and saved static/simpler setup exercised
current persistence guards. No app source/dependency/live-mode changes or live
calls; development DB hashes remained unchanged. Evidence includes the earlier
development-run DOM capture loss rather than inventing a value for it.

## Disabled provider adapter follow-up — October 26, 2026

See [adapter contract and tests](assignment3-part2-adapter.md). Live remains off;
all provider testing is simulated with MockTransport and temporary databases.
Run the existing full backend suite and frontend test/lint/build gates. New tests
in `backend/tests/skills/test_live.py` cover reservations, concurrency,
cancellation/deletion races, recovery, no write lock across provider waits,
structured parsing and default-disabled/disclosure gates. Composer/API tests
cover pending-state exact-ID retry, cancellation generation and mock fallback
labeling. Do not enable calls merely to run the routine verification suite.
The real model-contribution requirement remains unverified. The earlier browser
60.011-second result was not remeasured in this adapter step.

## Authorized live batch — October 26, 2026

[Four recorded real-model checks](assignment3-part2-live-checks.md) passed:
typing, motion choice, unsupported advice and fictional support reference. No
failed calls or retries occurred. The existing ledger moved from 0 to 4 reserved
attempts ($0.40); six/$0.60 remain. Mock mode was restored and checked through
the application status route; history reads made no further provider call.
Full mock regressions again passed: 492 backend, 85 frontend, lint and production
build. This is not a fifteen-case or repeated live-variation evaluation, nor a
live browser/clinical safety assessment. Further live calls need new authorization.
