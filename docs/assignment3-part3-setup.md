# Part 3 isolated fresh setup — November 2, 2026

**Initial attempt — historical partial pass.** Fresh declared dependencies installed and
normal startup/frontend checks passed, but the full backend suite had 130 setup
errors. This is an unpublished working-files snapshot, **not a committed clean
checkout**. No application source/dependency declaration/lockfile was changed.

Latest follow-up: the [test-only compatibility repair](assignment3-part3-compatibility.md)
now passes all 492 backend tests in this same isolated environment. All eleven
npm findings were triaged. The [four subsequently approved updates](assignment3-part3-dependencies.md) now pass the isolated gate and are in the repository lock; seven moderate lint-tool findings remain. The initial failures
and unchanged initial evidence below are retained.

## Isolation and installation

Copied 235 tracked and nonignored current files to
`/private/tmp/hudson-part3-setup-20261102`, excluding separate submission outputs.
No .git, .env, original database, virtual environment, node_modules, build or
cache was copied. [Snapshot manifest](../evidence/assignment3-part3-setup/snapshot.json)
records the base Part 2 SHA and exact copied hashes; it does not label that SHA
as evaluated Part 3 code. Later report edits are outside this source snapshot.

Used Python 3.14.7, Node 24.20.0 and npm 11.19.0. Followed README virtualenv,
`pip install -r backend/requirements.txt`, `npm install` and startup commands.
Download caches were inside the temporary copy. The initial restricted downloads
failed DNS resolution; authorized registry access succeeded. No pip upgrade,
audit fix, undeclared direct dependency or original-environment install occurred.
Only declared packages and their resolved transitive dependencies were installed.
Python requirements are unpinned; this install resolved pytest 9.2.0, FastAPI
0.162.0, Starlette 1.10.0 and Pydantic 2.14.2. `pip check` passed. Copied package
lock and all snapshot inputs remained hash-identical. Version lists are evidence.

No credentials are needed for these mocks/travel CSV checks. No .env was created;
backend mode was explicitly `SKILLS_MODEL_MODE=mock`, with health confirming
unconfigured credentials. Newly created databases lived only under the temporary
copy. The original ledger remained eight/$0.80 reserved, two/$0.20 available.
The temporary skills ledger had zero reservations and only a completed mock run;
it was never used to send a paid call or replace/refill the original ledger.

## Checks and observations

| Check | Result |
| --- | --- |
| Documented backend pytest command | 362 passed, 130 setup errors |
| Frontend tests | 87 passed |
| Oxlint / ESLint without fixes | Both passed |
| Production build | Passed, Vite 8.2.2, 53 modules |
| README backend reload and frontend dev startup | Passed after local-port permission |
| Health / model status / skills sessions | HTTP 200, mock mode |
| Travel success / unmatched / blank API | 200 two stays / 200 empty / 400 validation |
| Six travel browser inputs | Exact, lowercase, trimmed, partial show T001/T009 and $150; unmatched/blank clear stale results |
| Skills browser | Mock disclosure and saved fixed reply; Start/Pause/Stop; support Back remains paused |

The first matching browser snapshot was taken before all results appeared;
explicitly waited for the visible two-stays message and rechecked all four
matching variants. Browser support controls were only opened locally; no resource
link/provider/ZIP/advisor action was activated. No new complete-duration timing
is claimed. The fresh 60.005-second result remains the preceding evaluation.
No saved original sessions/conversations/preferences were used or cleared.

## Reproduced backend blocker and install advisory

A minimal fresh-process reproduction confirms `skills_database_path` exists
before `MonkeyPatch.setattr`; after `undo()` it no longer exists. The installed
pytest 9.2.0 implementation records the instance __dict__ entry for undo, while
Starlette State dynamically stores the attribute in `_state`. Repeated test
fixtures therefore lose required settings after cleanup. This is a reproduced
test-tool/fixture compatibility issue; it does not establish a broken production
state object. Direct app startup/HTTP/browser behavior passed. Disabling pytest
and Pydantic plugin loading still gave 2 passed/23 errors in the conversation
file, so that diagnostic did not fix it. No fixture/library patch or version
pin/downgrade was made as part of this verification-only step.

npm install also reported **11 advisories: seven moderate, three high, one
critical**. These are installer-reported counts, not an independently reviewed
exposure assessment. No audit fix/upgrade was attempted. Triage remains open;
do not claim fresh setup is fully ready or that the report establishes deployment
security. Address this and the backend errors before the final readiness gate.

## Preservation and evidence

Original database/.env/CSV/prior-report hashes and durable allowance match before
and after. All snapshot inputs are unchanged. Only the test backend reloader,
its child and frontend were stopped; ports 8000/5173 were then free. Test tab
closed. No live call, commit, push or submission occurred.

- [Results and limits](../evidence/assignment3-part3-setup/results.json)
- [Backend output](../evidence/assignment3-part3-setup/backend-tests.txt)
- [Frontend output](../evidence/assignment3-part3-setup/frontend-checks.txt)
- [Minimal undo reproduction](../evidence/assignment3-part3-setup/pytest-reproduction.json)
- [Plugin-disabled diagnostic](../evidence/assignment3-part3-setup/diagnostic-plugin-disabled.txt)
- [Python versions](../evidence/assignment3-part3-setup/python-versions.json), [freeze](../evidence/assignment3-part3-setup/python-freeze.txt), [npm tree](../evidence/assignment3-part3-setup/npm-tree.json)
- [HTTP observations](../evidence/assignment3-part3-setup/endpoints.json)
- [Browser observations](../evidence/assignment3-part3-setup/browser-observations.json), [mock screen](../evidence/assignment3-part3-setup/mock-startup.jpg)

Next: a separately requested focused compatibility fix and advisory triage,
then rerun the isolated gate. A final committed checkout and recordings/code
explanation still require their own verification.
