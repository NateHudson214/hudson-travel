# Assignment 3.3 — Part 3 report draft

Readiness reviewed November 2; both actual recordings sample-reviewed November 3, 2026. **Implementation/evidence and local media reviewed; NOT ready for
submission.** Full final playback/access checks and the exact committed-checkout gate,
published SHA and final report/checkpoint decisions remain pending. Hosted media links are supplied; the student confirms instructor viewing permission.
The seven moderate lint-tool findings remain explicitly unresolved.

Repository: [NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel).
Branch: `codex/assignment3-part3-refinements`.
Submitted Part 3 commit: **PENDING**. Base Part 2 checkpoint
`16deb696c24222519c88be73f6d29df1a3fbab76` is not a Part 3 submitted version.
Finished demo: [Demo A — application demonstration](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/nwh5289_psu_edu/Documents/assignment3-part3-demo.mov?d=w21c40828f8a64f588991bf457f26ed6a&csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=YbTWlA).
Process/code explanation: [Video B — failure, evidence, decision and code](https://pennstateoffice365-my.sharepoint.com/:v:/r/personal/nwh5289_psu_edu/Documents/assignment3-part3-process.mov?d=w5559618d638c49dead9c73406d8b99e0&csf=1&web=1&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=KscKse).

## Completed experience and refinement

The separate Vue/FastAPI/SQLite skills view supports one application-owned paced
breathing skill: six four-second-inhale/six-second-exhale cycles. Optional
conversation sits before/after pacing. The user can Pause, Resume, Stop or Leave;
U.S. support information remains independently bundled and visible through the
exercised loading/failure/history states. No detector decides who may open it.
The prototype is for fictional coursework, not therapy, diagnosis or monitoring.

Part 3 revisits the [approved design](../../docs/assignment3-part1-experience.md):
simpler view now hides optional conversation entries until Show more, reducing
decisions (D1/D3) while retaining user choice (R4). Compact ready-screen display
Save/Use last setup/Reset remain so a simpler setup can still be saved (D5/R4
versus interface contraction). Existing chosen conversations are not forcibly
closed. Cancellation wording now refers to saved messages, matching the UI;
Leave cannot promise undo of already dispatched work.

Explicit saved display preferences reduce repeated choices without configuring an
emotional profile. Reading history or reloading does not apply choices or start
breathing. Use last setup applies only display settings; reduced motion has
precedence. Reset clears saved display choices separately from confirmed history
clearing. These choices preserve R3/R4 and D5 but add an explicit Save decision.
No typing/disclosure/rating is required during pacing (D2/D3); neutral fixed text
and optional static cues address D6. [Full R1–R4/D1–D6 tradeoffs](../../docs/assignment3-part3-readiness.md).

Reused Hudson Travel's FastAPI entry point/configuration, Vue/Vite/node:test and
lint tooling, shared JSON request helper, and patterns for injected transports,
short SQLite transactions, bounded history and error/restore handling. Skills
components/tables are separate adaptations; hotel prompts/model SQL, booking
semantics, course CSVs and original travel records are not part of skills logic.
[Technical organization/reuse](../../docs/assignment3-part1-technical.md).

## Model, persistence and user authority

The real adapter supplies the approved catalog, placement, relevant terminal
session facts, this conversation's bounded recent messages and explicit saved
display choices. It accepts reviewed reply/fact IDs and renders application text;
arbitrary model-written therapeutic prose is rejected. Timing, navigation,
preferences and independent support remain application/user controlled.
For fictional crisis references, the live selector prompt requests only the
reviewed support signpost; this is not a detector/assessment guarantee. The
independent route never depends on that selection. Default conversation is a
clearly labeled fixed mock that does not interpret messages. [Boundary and lifecycle](../../docs/assignment3-part2-adapter.md).

The separate local SQLite database stores sessions/checkpoints, fictional
conversation messages, run provenance/status, explicit display choices, a history
generation and durable allowance counters. History restores acknowledged records;
unfinished sessions do not resume automatically. Confirmed clearing advances the
generation so older writes fail, and preserves preferences and the allowance.
Plaintext local fictional records and unrecovered unsent drafts remain limits.

## Expected versus observed verification

| Evidence | Verified observation / limit |
| --- | --- |
| [Fifteen-scenario matrix](../../docs/assignment3-part3-evaluation.md) | S01–S15 pass under documented mock/browser/local-simulation conditions: ordinary before/after use, completion, pause/support/leave, invalid output, backend outage, preferences/reset, clear races and restart/history. Expectations were saved before execution. |
| [Three explicit checks](../../evidence/assignment3-part3-evaluation/results.json) | B1 independent safety/exit; B2 application/user authority; B3 durable limited writes. Not universal security or clinical proof. |
| [Fresh duration](../../evidence/assignment3-part3-evaluation/timing.json) | 60.005 s DOM active; 60.002 s clock/SQLite; 17.146 s setup; 12 ordered cues/six cycles; no pauses/support/model request inside the sequence. <=90 s in this one visible-browser/static-cue sample. |
| [Pause/support/restart records](../../evidence/assignment3-part3-evaluation/restart-outage.json) | Separate pauses/support and acknowledged unfinished checkpoint restored without auto-resume. Actual backend outage preserved draft and local support/Leave access. |
| [Clear/late-write evidence](../../evidence/assignment3-part3-evaluation/clear-verification.json) | Cancel preserved temporary data; confirmed deletion removed temporary history, kept preferences/ledger, rejected old generations; new-generation activity could save. Original history was not cleared. |
| [Actual Part 3 live batch](../../docs/assignment3-part3-live-checks.md) | Four real OpenAI gpt-6-luna attempts: typing twice and motion twice. One timeout (3066 ms route), then expected typing selection (1522 ms); both motion selections identical/expected (2693/1838 ms). No retries. |
| [Latest isolated gate](../../docs/assignment3-part3-dependencies.md) | 492 backend /87 frontend tests, non-fixing Oxlint/ESLint, Vite 8.2.4 build and travel/skills browser checks passed. Current lock matches the tested copy. |
| [Fresh setup and correction](../../docs/assignment3-part3-setup.md) | Initial 362 passes/130 fixture errors; one partial correction 444/48; mapping-based State patches resolved to 492 passes. Existing source snapshot/dependencies were isolated; not a committed clean checkout. |

Timing assumptions: no typing/user response during the guided skill, and setup
begins at ready-engine creation rather than cold asset loading. User-selected
pauses and resource access are excluded; application delay during pacing counts.
DOM telemetry is not hardware-paint/per-phase jitter proof. The recording must
show its own actual new values, not copy this earlier measurement.

Mock fixtures are labeled: S11 uses a JavaScript reduced-motion response, not an
OS-setting/CSS integration test; S12 uses temporary SQLite failure/promise
injection; S15 uses actual routes with local MockTransport and two fake dispatches,
not paid provider calls. Original databases/allowance were preserved for these.

The real repeated batch uses identical context per pair. Three received responses
reported gpt-6-luna; the timeout has only its configured identifier, no received
selection/usage. Motion shows two matching selections; typing has only one
successful selection to compare. Small samples do not establish reliability.
There are now eight total reserved attempts/$0.80 across Part 2 and Part 3,
leaving two/$0.20. Reservations are not billed cost; timeout usage is unknown.
Mocks were restored. No further live call is needed for the remaining review.

## Surprising finding, decisions and unresolved limits

A delayed mock still saved a completed pair after Leave returned the screen to
idle; the late response did not reappear in the abandoned UI. Retain immediate
exit, late-result/generation guards and accurate cancellation copy rather than
promise to recall dispatched work. The real timeout also exposed availability
cost in the three-second deadline: keep finite waiting and optional continuation,
and count failures instead of spending again to hide the result.

The test-only fixture repair patches State's actual mapping so cleanup restores
settings, with no production/version workaround. A separate 164-test diagnostic
confirmed every original app-state key/binding survives cleanup. Four approved
package updates were then verified/locked: Vite 8.2.4, shell-quote 1.11.0,
source-map-js 1.2.2, brace-expansion 5.0.12. Original frontend node_modules has not
been reinstalled; the new audit result applies to the matching isolated install.

**Seven moderate lint-tool package findings remain unresolved**, down from eleven
including high/critical findings. The minimatch fix is outside current parent
major ranges; no major override/downgrade was applied. Inspected lint paths use
default optimization level 1 versus the advisory's >=2 trigger and fixed globs;
this lowers observed exposure but does not patch the dependency or prove all
paths safe. [Investigation/evidence](../../docs/assignment3-part3-dependencies.md).
User direction to retain this limitation is not treated as acceptance or a fix.

Untested limits: actual OS reduced-motion/CSS integration, full screen-reader/
accessibility checks, hardware-paint/device/load timing and cold offline launch.
The 250 ms cue-delay threshold is provisional; Python requirements remain
unpinned. No peer/independent-person or exact committed clean-checkout run is
claimed. Software findings are not measures of clinical effectiveness.

## Recordings, disclosure and submission status

Two actual local recordings now have [sampled media reviews](../../docs/assignment3-part3-media-review.md):

- `assignment3-part3-demo.mov`: 307.345 s, 2866x1494, silent. Samples show skill
  completion, personalization/history, independent support and Leave. Its timing
  screen reads 60.02 s rendered, 60.01 s clock and 56.26 s setup, separate from the
  earlier instrumented sample. The bottom action bar is cropped; the student
  explicitly accepts this limitation and no retake is requested.
- `assignment3-part3-process.mov`: 202.530 s, 2866x1494, silent. Samples show all
  thirteen sections: actual saved failure/reproduction, correction/revised attempt,
  passing verification, generated timing/reply/deadline code and decisions/limits.
  It begins directly with the walkthrough, without the optional control supplement.
  The introduction's supplement reference is not claimed as captured app evidence.

Review used 32 A /22 B ten-second samples and selected full-resolution frames,
not continuous playback or all-frame privacy certification. The important error/
code text inspected is readable. Optional B cleanup is to remove the inaccurate
intro reference and trim recording controls at its tail. Both originals are
unchanged. The student supplied hosted OneDrive links above and confirms that the
instructor/applicable graders can view both. The agent browser reached Penn State
sign-in for both links; it did not independently play the hosted copies or verify
that their bytes match the reviewed local originals. [Link-check record](../../evidence/assignment3-part3-media-review/hosted-links.json). Full final playback is a manual check.

[Demo script](../../docs/assignment3-part3-demo-script.md),
[process script](../../docs/assignment3-part3-process-script.md),
[caption cards](recording-cards.html) and [source/evidence walkthrough](process-walkthrough.html)
remain supporting artifacts, distinct from the actual recorded files. No old
Assignment 2/Part 2 recording is relabeled as Part 3.

[AI-USE](../../AI-USE.md) and [curated evidence log](../../evidence/assignment3-part3-log.md)
record tools, failures/revisions and limits. The student-reported drafting model
is GPT-6.1 Sol with medium effort; app/runtime version was not independently
rechecked. Actual skills API identifiers and fixed mocks are distinguished.

Next: finish final playback/report decisions, retain unresolved limitations,
authorize final checkpoint and an exact committed-checkout gate, verify the final
published SHA and accessible pinned evidence/media links, then manually submit
one separate upload-ready Part 3 report. [Readiness matrix and exact steps](../../docs/assignment3-part3-readiness.md).
[Read-only final-review evidence](../../evidence/assignment3-part3-readiness/review.json).
No installation, provider call, commit, push, upload or Canvas submission occurred
in this readiness review; original protected files and allowance are unchanged.


## Authorized checkpoint — November 3, 2026

The student approved this report and its documented limitations, including the
seven unresolved moderate lint-tool findings, and authorized the reviewed commit,
exact committed clean-checkout verification and conditional branch publication.
Precommit mocks passed 492 backend/87 frontend, non-fixing lint and Vite8.2.4
build. This source document is the reviewed checkpoint draft; the separate
publication upload report will contain the actual full commit and post-commit
clean-checkout result. No submitted SHA or future result is invented here.
