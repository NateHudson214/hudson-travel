# Assignment 3 Part 2 — Final readiness review

Finalized October 27, 2026, America/New_York, using the October 26 live checks.
**Core Part 2 behavior has evidence; student approval received October 27.**
The student accepted the disclosed UI/design limits and authorized checkpoint
checks, commit and branch publication. The separate upload copy still needs its
real checkpoint metadata/pinned links. Checkpoint publication and pinned-link/grader-access checks are recorded separately
after the commit exists; this source review does not assert those future results.
Mock mode is enabled; this review made zero additional provider calls. The durable
ledger remains four reserved attempts/$0.40, leaving six attempts/$0.60. This is
reserved allowance, not actual billing. No application source/dependency change,
commit, push, visibility change, upload or submission occurred.

## Assignment and approved-design check

The supplied full assignment requires a working Vue/FastAPI/SQLite localhost
skill, actual contextual model contribution, persistent session/conversation
history, a measured <=90-second guided exercise, independent crisis information,
failure/exit behavior, research reasoning and an honest milestone report.
The fifteen-scenario/repeated-live-variation evaluation, clean-checkout
verification, finished-demo/process recordings and code explanation are Part 3.
A video is not explicitly mandated by the Part 2 implementation paragraph;
add a Part 2 walkthrough if separately directed by the instructor or chosen.

| Part 2 criterion | Verified evidence | Verdict / scope limit |
| --- | --- | --- |
| Complete at least one intact skill | Six 4-second inhale/6-second exhale cycles; earlier 12-cue completion capture | Met for breathing; only one skill is offered. |
| Contextual conversational model | Four real OpenAI gpt-6-luna replies selected expected approved IDs/facts; one follow-up used earlier history | Basic contribution evidenced; single samples, not a reliability/clinical claim. |
| Application-owned boundaries | Strict renderer, versioned instructions/catalog, no model timing/navigation/preference authority | Met; structure cannot guarantee correct selection. |
| Session/conversation SQLite persistence | Earlier completed session restart/history inspection; four actual live runs/eight messages/three conversations restored | Met; plaintext fictional local records, no accounts. |
| Useful history | On-demand summaries/detail; current UI read-only review correctly labeled actual replies “Reviewed model selection” | Met; exact run statuses are exposed by API/SQLite, not the history UI. |
| Measured guided duration | Earlier production-preview 60.011 s DOM-observed active / 60.010 s clock, 12.055 s setup | Met in that observed sample; no fresh duration or device-wide guarantee asserted. |
| Independent crisis route and exit | Bundled support after malformed mock, during pacing, and with backend truly stopped; immediate Leave | Met in reviewed browser; external services were not contacted/tested. |
| Failure behavior | Application fallback on invalid selection; real outage retains draft/error; paused return requires Resume | Met; live failure races tested with deterministic mocks, not paid fault injection. |
| Personalization/control | Explicit Save/Use last setup/Reset and separately confirmed Clear history; no automatic start/reuse | Met for limited display personalization; one extra save action. |
| Research reasoning and tradeoffs | All R1–R4/D1–D6 mapped below and in report/approved notes | Met as explanation; simpler view still differs from proposal. |
| Guidance, AI-use, curated revised approach | README/AGENTS/AI-USE, step guides, failed-capture/query-contract evidence | Present; no invented provider failure or recording. |
| Submitted version/evidence access | Existing HEAD remains Part 1 e871cadc06d46398709d688df41de350d71c7f5b | Pending reviewed Part 2 commit, publication, pinned links and grader access. |

## Disclosed UI/design differences accepted for Part 2

The student explicitly accepted these scope/quality limits when authorizing the
checkpoint on October 27. Application behavior was not silently changed; future
refinements require their own implementation/verification step.

1. **Simpler view contracts less than proposed (D1/D3).** It hides history,
   pacing configuration and explanatory text, but still shows optional conversation
   and Save/Reset controls. The approved Part 1 sketch proposed hiding conversation
   suggestions behind Show more. The current view retains discoverability/control
   at the cost of more visible choices. The final browser check confirmed this;
   see [the actual screen](../evidence/assignment3-part2-final-review/simpler-view.jpg).
   Accept this limited Part 2 tradeoff or request the contraction refinement.
2. **Cancellation/history copy is broader than the displayed history.** Live
   composer text says to review saved statuses in history. History labels message
   origin/fallback and shows text; it does not render pending/cancelled/failed run
   status badges. The records/status API do retain those states. Do not claim
   those badges were implemented; refine the copy or status display later.
3. **Timing limits.** Setup starts at ready-view/engine creation, including chosen
   setup/conversation time, not cold navigation/asset loading. The 60.011-second
   measurement is an earlier DOM observation, not hardware-paint telemetry or a
   guarantee under load. Per-phase render jitter, the provisional 250 ms delay
   threshold and multi-device timing have not been empirically validated. The
   retained timer code is unchanged; no new completion time is fabricated here.
4. **Stored state and recovery.** Explicit Save replaces the Part 1 automatic
   remembering proposal, at the student's request. History stores acknowledged
   checkpoints; close/crash may lose unsent drafts/queues. Interrupted-session
   reconciliation is explicit so one tab does not stop another. Before chat can
   be unlinked; after chat links only when its session save was acknowledged.
5. **Verification scope.** Live sends were headless real-route/real-HTTPS calls,
   not a live browser Send demonstration. This review did inspect the actual live
   replies in browser history with provider calls and write requests blocked.
   OS reduced-motion toggling, screen readers/full accessibility, cold-offline
   frontend launch, external contact handlers and broader model variation remain
   unverified. The development view previously reset for an unestablished reason;
   the final production-preview checks were stable. No root-cause fix is claimed.

## R/D reasoning and tradeoffs

| Finding | Implementation and reason | Tradeoff |
| --- | --- | --- |
| R1 | Short fixed sequence, no chat/input inside pacing | One measured run is not a timing guarantee. |
| R2 | Support control directly opens bundled U.S. information | External connectivity/service operation remains separate. |
| R3 | Stop/Leave without explanation, penalty, rating or confirmation | Accidental stopping can occur; restart is explicit. |
| R4 | Optional chat/history/reuse, explicit Start/Resume and display actions | One skill limits choice; unsupported requests receive scope text. |
| D1 | Manual simpler view, never inferred distress | It retains more optional controls than the approved sketch. |
| D2 | One current phase/action, chat outside the guided sequence | Stable support/exit/pause controls are intentional exceptions. |
| D3 | No required typing/disclosure/rating during exercise | Entry can still ask the user to consider optional controls. |
| D4 | Support survives exercise, failed requests, history and confirmation | No claim that local information proves external help availability. |
| D5 | Voluntary saved display setup/reuse/reset, no inferred effectiveness | Explicit save costs a click; display adaptation is narrow. |
| D6 | Neutral application text, muted UI, static/reduced-motion precedence | No completed full accessibility or emotional-cost study. |

## Final no-call browser/record checks

Used the already built production preview, actual FastAPI app, temporary databases
and an explicit invalid mock fixture. Providers/keys were unavailable in this
harness. A second read-only review server read the existing real skills history,
blocked all non-GET requests and kept providers disabled. This did not copy/reset
its allowance. The original skills database hash was unchanged after the review.

| Check | Expected | Observed |
| --- | --- | --- |
| F1 Simpler ready view | Reduce secondary content, keep safety/exit/Start | History/explanations hidden; conversation and Save/Reset still visible (design difference). |
| F2 Invalid mock selection | Reject free prose, fixed fallback | Failed mock run/application fallback; unapproved fixture text absent from SQLite. |
| F3 Start/support/Back | Pause and stay paused until explicit Resume | Current phase retained; Back showed Resume/Stop and stayed paused. |
| F4 Resume/Stop | Explicit continuation, immediate stop | Exercise stopped; stopped record saved. |
| F5 Genuine backend outage | Draft/error retained; independent support/Leave | Send failed with backend stopped; draft remained, local support opened, Leave showed idle. No retry was invoked. |
| F6 Actual saved live history | Correct text/provenance without a new call | Typing/follow-up and motion conversation restored, labeled Reviewed model selection. |
| F7 No unintended state/calls | Remain mock, original ledger/data unchanged | Original DB hash unchanged, four live runs remain, no pending runs or new reservations. |

Evidence: [fallback](../evidence/assignment3-part2-final-review/fallback.jpg),
[offline error](../evidence/assignment3-part2-final-review/offline-error.jpg),
[offline support](../evidence/assignment3-part2-final-review/offline-support.jpg),
[actual live reply in history](../evidence/assignment3-part2-final-review/live-history.jpg),
[temporary mock records](../evidence/assignment3-part2-final-review/mock-records.json),
[review verification](../evidence/assignment3-part2-final-review/review-verification.json).
Only the review's test services/tab were started/stopped; no service contact.

The unchanged source most recently passed **492 backend tests, 85 frontend tests,
non-fixing oxlint/ESLint and a 53-module production build** after the live checks.
This documentation/UI review did not rerun those identical suites; its source
fingerprint still matches that tested code. Two existing dependency deprecation
warnings remain. No dependency was installed/upgraded.

## Evidence checklist and remaining actions

See the [final report draft](../assignment3/part2/report.md) and
[exact checkpoint/submission checklist](assignment3-part2-submission-checklist.md).
The report is a finalized review draft, not an upload-ready artifact: its Part 2
commit remains PENDING and local links must be replaced after publication.

Student acceptance and checkpoint authorization are now recorded. Mock-only
checkpoint checks passed again (492 backend/85 frontend, lint/build). Complete
the authorized commit/publication and remote verification next. Generate a separate
upload-ready report.md afterward with the actual checkpoint and absolute pinned
links; verify grader access; manually upload to Assignment 3.2 and confirm receipt.
Do not substitute the Part 1 HEAD, change visibility, merge or submit automatically.
No further live call is required for these steps.

Part 3 remains: a formal >=15-scenario expected/observed table with three behavior
checks, a small relevant repeated live selection within a newly authorized
remaining allowance, finished demonstration/process/code-explanation recording,
refinement and clean-checkout verification. Existing test totals/four live cases
are not a claim that those Part 3 deliverables are complete.

Earlier review observations remain in the curated process log and step guides;
this final review supersedes their older blocker lists and next prompts.
