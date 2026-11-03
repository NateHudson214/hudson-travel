# Assignment 3 Part 3 final readiness review

Reviewed November 2, 2026 against the full student-uploaded assignment and
supplied R1–R4/D1–D6 table. **Implementation/evidence review complete; submission
not ready.** Final media playback, committed-checkout verification,
publication/access and final report decisions remain. Seven moderate lint-tool
findings stay explicitly **unresolved**, as requested; no acceptance or fix is
inferred. This review made no installation, live call, commit, push or submission.

November 3 media update: both actual recordings received a [sampled review](assignment3-part3-media-review.md). A is 5:07 and B is 3:23; core demo and process/failure/code content is present. The student accepts A's framing as-is, so no retake/supplement is required. The student supplied both hosted OneDrive links and confirmed instructor/applicable grader viewing access. Agent browser checks reached sign-in only; full final hosted playback and exact committed-checkout/publication gates remain. The agent has not uploaded or submitted anything.

## Assignment requirements versus verified evidence

| Requirement | Verified result | Remaining gap / limit |
| --- | --- | --- |
| Complete/refine at least one intact skill in Vue/FastAPI/SQLite on localhost | Six application-owned 4/6 cycles; separate skills view/database; latest browser and regression evidence | No clinical-effectiveness claim; no additional skill required. |
| Revisit Part 3.1 choices and explain changes | Simpler view now hides optional conversation until Show more; compact ready display controls retained as D1/D5/R4 tradeoff; saved-message cancellation wording; test fixture repair and four approved lock changes | No automatic distress detector or model control of timing/preferences. |
| Relevant model/context contribution | Reviewed reply/fact selector, bounded recent conversation/session/saved display context; four real Part 3 dispatches | Three expected selections, one timeout; only one successful typing selection. Headless checks, not live browser Send. No more calls needed for this review. |
| Session/conversation persistence and useful history | Fifteen-case browser/SQLite evidence includes restart, restored text, acknowledgments and interrupted session; optional display Save/Use last setup/Reset | Plaintext local fictional data, no accounts, unsent drafts not recovered after closing. |
| Personalization, control and effort reasoning | Explicit saved display choices only; reuse never starts; no automatic emotion inference; history clear separate from reset | Explicit Save adds effort; compact controls in simpler ready view add choices. These are documented tradeoffs. |
| Guided duration <=90 s, setup separate, pauses/support excluded | Fresh visible-browser/static run from first paced cue through final planned step: 60.005 s DOM active, 60.002 s clock, 17.146 s setup, 12 ordered phase cues, six cycles; separate pause/support measurements | One sample; setup begins at ready-engine creation, not cold load; no hardware-paint/per-phase/device-load guarantee. No new timing run in this review. |
| Crisis route throughout, independent of model/failure | B1 covers exercised ready/running/paused/waiting/failure/history/confirmation states; genuine backend outage with bundled panel and Leave | U.S. scope labeled; contacts previously checked. No services contacted; cold offline frontend launch untested. |
| Crisis-related fictional input policy | Live selector prompt requests the reviewed support_signpost, with no assessment/monitoring claim; fixed mocks do not interpret input. Independent bundled support is always available regardless of selection/failure. | Prompt selection is not a detector guarantee. Earlier Part 2 one-off signpost evidence is not a new Part 3 call. |
| At least 15 fictional scenarios, expected and observed | S01–S15 recorded, expectations saved before execution; all pass under stated mock/browser/local simulation conditions | S11 JavaScript reduced-motion fixture, S12 trigger/promise injection, S15 local fake transport explicitly labeled; not all OS/paid cases. |
| Three explicit checks across cases | B1 independent safety/exit, B2 application/user authority, B3 durable/limited writes | Finite tested states, not universal security/accessibility/clinical proof. |
| Repeat a small relevant live selection to inspect variation | Typing twice, motion twice; same context per pair; no retries; failed attempt counted | Two identical successful motion selections; typing timeout prevents two successful selections. Preserve the observed failure. |
| Surprising finding and untested limitation | Delayed mock can save after immediate Leave; real provider timeout; explicit cancellation/latency decisions | OS reduced-motion/CSS, full accessibility, cold offline and device/load timing remain untested. |
| Verify another person can run a clean checkout using README | Fresh isolated declared dependencies, fixed test compatibility, latest approved lock, full gates and normal startup/browser verified | Unpublished snapshot is not a committed clean checkout. No peer/independent-person run or final committed setup result is claimed. |
| Finished app demo and process screencast with generated-code explanation | Actual A (5:07) and B (3:23), silent, sampled review shows app behavior and failure/evidence/decision/generated-code sections | Student accepts A framing; no retake required. Hosted URLs are supplied with student-confirmed instructor Can view access; agent playback reached sign-in only, full final playback remains manual. |
| Repeatable tests and AI-use/evidence practices | Latest isolated 492 backend/87 frontend, non-fixing lint and Vite 8.2.4 build; actual failures and revisions retained; AI-USE names user-reported GPT-6.1 Sol medium and observed API gpt-6-luna | Runtime drafting-model identity/app version not independently rechecked; retain disclosure caveat. |
| One report.md with repository, submitted commit and accessible relevant links | Separate Part 3 report exists; Part 1/2 preserved | **Submitted SHA, commit-pinned repository/evidence URLs and published-repository grader-access checks pending.** Hosted video URLs supplied with student-confirmed viewing permission. No Canvas upload. |

Sources: [mock matrix/method](assignment3-part3-evaluation.md),
[live results](assignment3-part3-live-checks.md),
[isolated setup](assignment3-part3-setup.md),
[fixture correction](assignment3-part3-compatibility.md),
[approved dependencies](assignment3-part3-dependencies.md),
[read-only review checks](../evidence/assignment3-part3-readiness/review.json).

## Research reasoning and reuse check

| Finding | Implemented decision and tradeoff |
| --- | --- |
| R1 | Fixed 60-active-second sequence, separately measured setup. Conversation/setup can add overall visit time; do not equate exercise timing with total visit time. |
| R2 | Persistent independent support control, including observed failures; no classifier gate. U.S.-only bundled information is explicit. |
| R3 | Pause/Stop/Leave and optional conversation; no completion reward/penalty. Leave cannot promise undo of already dispatched work. |
| R4 | User chooses simpler/static/reuse/start/resume/exit; model does not route or change settings. More choice can add setup effort. |
| D1 | User-chosen simpler view contracts optional entries; no assumed distress signal. Compact display controls remain to let a simpler setup be saved. |
| D2 | One guided skill/phase at a time; conversation remains outside pacing. Ready view still has setup choices. |
| D3 | No required typing/disclosure/rating during exercise; optional mock conversation. Explicit saving is predictable but adds a button decision. |
| D4 | Locally bundled visible safety access; Back stays paused. Opening the external service itself needs phone/internet. |
| D5 | Optional saved display reuse and local history, no automatic configuration/emotion adaptation. Does not predict the user's preferred skill. |
| D6 | Short application-owned neutral text, muted presentation, static/reduced-motion precedence. No completed reader/accessibility/emotional-cost study. |

Reuse is the existing FastAPI entry point, Vue/Vite/node:test/lint tooling,
backend-only configuration, shared requestJson helper, and the hotel work's
transport injection, bounded-history/short-transaction and restore/error patterns.
Skills modules/storage were adapted separately; they do not call the hotel SQL
chatbot, use its hotel prompt/booking semantics or write its CSVs/database.
This is pattern/tooling reuse, not wholesale identical component reuse.

## Outstanding decisions

- Keep the seven moderate lint-tool findings unresolved in the submitted draft;
  decide later whether to seek further supported remediation or explicitly accept
  the documented coursework limitation. User direction to document them does not
  mean a major override is authorized or the package is patched.
- Record two silent videos using readable captions/code, or combine them with
  clearly marked sections. No narration requirement appears in the supplied text;
  quality must still demonstrate understanding. Choose actual hosting and access
  permissions after the files exist. Do not expose/deploy the app as support.
- Approve the final report/limitations and the exact scope of checkpoint work
  only after media and remaining gates are reviewable. No new paid test is needed.

## Exact remaining checkpoint and submission sequence

1. **Final playback and media links.** Both actual recordings exist, were sample-reviewed and now have student-supplied hosted links with confirmed instructor viewing permission; no A retake is required. Watch both complete final hosted files; agent checks reached sign-in only. The prepared routes remain available for reference: [demo A](assignment3-part3-demo-script.md)
   and [process/code B](assignment3-part3-process-script.md). Caption file:
   `assignment3/part3/recording-cards.html`. Browser-tool local HTML preview was
   blocked by protocol policy; static syntax was checked, but visual review is
   pending. Open the file normally from Finder if supported; if your browser
   disallows it, do not bypass a warning—use the scripts' readable caption text.
   Actual durations/names are recorded in the media review. Check the complete final files and correct
   unreadable/misleading cuts. A new complete demo run must show its own measured
   values rather than copying 60.005/17.146 from earlier evidence.
2. **Resolve final-report decisions.** Review the truthful live-timeout limitation,
   seven unresolved advisories, test/simulation limits and remaining setup gate.
   Supplied media links are in the Part 3 report and [link-check record](../evidence/assignment3-part3-media-review/hosted-links.json). Instructor permission is student-confirmed; no hosted playback or byte comparison is claimed. No agent upload occurred.
3. **Authorize a concrete checkpoint.** Stay on
   `codex/assignment3-part3-refinements`. Review the diff and evidence inventory;
   include only reviewed Part 3 implementation/tests, four-package lock change,
   documentation and curated evidence. Exclude .env, ignored original DBs,
   node_modules/.venv/dist/caches, temporary harnesses and unrelated submission
   outputs. Preserve old reports. Do not merge or change visibility.
4. **Run the checkpoint gates and commit only when authorized.** The verified
   original node_modules still has older packages, so do not mislabel it as the
   Vite 8.2.4 gate. Use a matching isolated dependency environment and verify its
   source/test/lock fingerprints. Require 492 backend/87 frontend, non-fixing
   linters/build, whitespace/link/protected-file checks or explain any real
   subsequent count change. Then create the reviewed local commit and capture
   its actual full SHA. No commit is authorized by this document.
5. **Verify the exact committed checkout before publishing.** Separate explicit
   authorization must cover extracting/checking out that actual commit into an
   empty isolated folder, installing only declared dependencies there, creating
   new temporary DBs and following README startup/checks. Keep mocks/key-free.
   Do not claim a copied working tree or reused environment is a committed clean
   setup. Record versions and results. If a fix is needed, review/recommit and
   verify the final SHA; never submit a different unverified head. A peer run can
   strengthen the “another person can run it” claim but has not occurred.
6. **Publish only when separately authorized and gates pass.** Push the reviewed
   branch to origin, without merge or visibility change. Verify the remote SHA
   equals the final tested SHA. Generate a separate
   `submission/assignment3-part3/report.md` with that exact checkpoint and
   absolute links such as
   `https://github.com/NateHudson214/hudson-travel/blob/<ACTUAL_SHA>/docs/assignment3-part3-readiness.md`.
   The angle-bracket example is a template, not a valid submission URL. Pin
   design, evidence, AI-USE and source links too. Do not upload this draft or an
   earlier Part 1/2 report. Keep the upload copy separate to avoid a self-SHA loop.
7. **Manual access verification.** Use the instructor's intended access context to
   open the repository, pinned design/matrix/evidence/source pages and play both
   actual videos beginning to end. Check media permissions/expiration/captions.
   A link that works only while signed in as the student does not prove grader
   access. Private repo access is not a reason to change visibility automatically.
8. **Manual Canvas submission.** Open the supplied
   [Assignment 3.3 Part 3 submission](https://psu.instructure.com/courses/2484533/assignments/18674750).
   Select the separate final Part 3 upload-ready `report.md`; confirm repository,
   full SHA and actual media/evidence links. Submit yourself, then download/open
   the submitted report and verify its version and the Canvas confirmation.
   No Canvas action has occurred in this review.

Current evidence is sufficient to prepare recordings/final decisions. It is not
permission to publish, proof of media, or a claim that every submission gate passed.


## Authorized checkpoint — November 3, 2026

The student approved this report and its documented limitations, including the
seven unresolved moderate lint-tool findings, and authorized the reviewed commit,
exact committed clean-checkout verification and conditional branch publication.
Precommit mocks passed 492 backend/87 frontend, non-fixing lint and Vite8.2.4
build. This source document is the reviewed checkpoint draft; the separate
publication upload report will contain the actual full commit and post-commit
clean-checkout result. No submitted SHA or future result is invented here.
