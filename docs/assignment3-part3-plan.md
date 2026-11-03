# Assignment 3 Part 3 — Refinement and evaluation plan

Started November 2, 2026. Current status: first refinement and all fifteen mocked
scenarios/B1–B3 and the four-attempt repeated live batch are evaluated. Clean checkout, recordings
and final submission remain incomplete. Branch:
`codex/assignment3-part3-refinements`, starting from Part 2 checkpoint
`16deb696c24222519c88be73f6d29df1a3fbab76`.
Preserve the Part 1/Part 2 reports and separate upload files. The existence of a
Part 2 recording/script is not proof that a final Part 3 recording was made.

Current [final readiness checklist and recording scripts](assignment3-part3-readiness.md)
identify the remaining media, unresolved lint findings and committed-checkout/
publication/access gates. Scripts are not completed recordings.

## Scope and changes from Part 1/Part 2

Keep one skill: six four-second-in/six-second-out cycles. No added skill, detector,
clinical claim or model authority over pacing/navigation/preferences. Skills
remain a separate view/database with travel behavior intact.

Part 2 exposed optional conversation in Simpler view, contrary to the original
experience sketch. Part 3 now hides its entry before/after the exercise until
Show more is chosen. Pacing/paused views still have no conversation entry. This
reduces optional decisions (D1/D3) without eliminating explicit access (R4).
A conversation already chosen is not forcibly closed by a display toggle.

The ready view deliberately retains compact Save/Use last setup/Reset controls.
Hiding them whenever simpler=true would make saving that very setup difficult.
This is a documented D1/D5/R4 tradeoff, not a claim that every secondary control
has disappeared. They do not appear inside the guided exercise. History and
longer explanations remain hidden in simpler mode; safety/Leave stay available.
Explicit Save remains the student's earlier choice rather than inferred emotion
or automatic preference persistence. Reset/history clear remain separate.

Live cancellation copy now directs users to saved **messages**, not status badges
that the history UI does not display. Backend run statuses/cancellation/clear-safe
storage remain unchanged. No new data fields, schema or provider request changed.

The November 2 contact lookup returned the same bundled U.S. contacts/scope. No
service was called/texted/chatted. Contact strings and their earlier full-review
version/date were not changed; there was no new official-page navigation test.

## Opening-step verification (historical scope)

These bullets describe the first refinement check. The subsequent full evaluation
completed its pending browser coverage and fresh timing; see the linked matrix.

- Optional conversation hidden in simpler ready/stopped views and restored by
  Show more without starting breathing: browser observed.
- Completed-state visibility and invalid/running/paused/history routing:
  visibility-policy tests pass; fresh completed-browser coverage still belongs
  in the formal scenario run.
- Simpler setup can still be explicitly saved; engine stays ready: browser observed.
- Support opens during pacing; Back stays paused; Stop works: browser observed.
- Safety/Leave DOM bounds remain inside the 1280-pixel browser viewport. Captured
  native screenshots show a cropped portion of that viewport, so they do not
  independently establish all viewport edges or mobile accessibility.
- Cancellation copy: source reviewed and production compilation passed. No live
  composer was enabled merely to observe this low-impact wording change.
- Full regressions: 492 backend tests, 87 frontend tests, non-fixing oxlint/ESLint
  and the 53-module build passed. Existing two backend deprecation warnings remain.
- Browser used actual app/production preview with temporary travel/skills DBs,
  no keys and a forbidden provider transport. No real/model call occurred.

Evidence: [simpler ready](../evidence/assignment3-part3-step1/simpler-ready.jpg),
[saved simpler setup](../evidence/assignment3-part3-step1/saved-simpler-ready.jpg),
and [step verification](../evidence/assignment3-part3-step1/verification.json).
The step did not remeasure a full exercise; earlier Part 2 timing is background,
not a new Part 3 result. The 250 ms delay threshold is still provisional.

## Remaining sequence

1. **Completed mocked evaluation:** [all fifteen scenarios/B1–B3](assignment3-part3-evaluation.md)
   passed under documented browser/temp-DB/simulation conditions. Fresh timing:
   DOM 60.005 s, clock 60.002 s, setup 17.146 s; twelve cues/six cycles. Expected
   outcomes were preserved before execution. This is not real live variation.
2. Review any failures and refine only what the evidence justifies. Record a real
   surprising finding and a limitation; do not invent a failure for a recording.
3. **Executed:** [four authorized repeated live attempts](assignment3-part3-live-checks.md):
   three expected selections, one timeout, no retries; mock restored. Both motion
   selections matched; only one typing selection completed. Retain this limitation.
4. [Authorized fresh setup attempted](assignment3-part3-setup.md) in an isolated
   unpublished snapshot with new declared dependencies. Frontend/startup/browser
   passed; backend 362 passed/130 errors and npm advisories require follow-up.
   [Fixture repair now passes 492](assignment3-part3-compatibility.md); all npm
   findings are triaged; [four approved updates](assignment3-part3-dependencies.md)
   pass the isolated gate and are locked, leaving seven moderate lint-tool findings.
   A committed clean checkout
   is still separate and unverified.
5. Prepare the final demo plus process/failure/evidence/decision and relevant
   generated-code explanation. The student previously requested silent recording;
   use readable written callouts/captions if retaining that format. Actual media,
   understandable code explanation and grader-accessible links remain pending.
6. Finalize `assignment3/part3/report.md`, AI-USE and curated evidence. Only after
   review/authorization, create/publish a final checkpoint and a separate pinned
   upload report. No commit/push/submission is part of this first step.

## Live allowance and preservation

The original ledger now has eight reserved calls/$0.80, leaving two/$0.20.
This is conservative reservation accounting, not billed cost. Do not reset it or
use a fresh DB to evade it. Temporary databases are only for deterministic tests.
Keep live disabled until a separately authorized bounded batch. Preserve original
travel/skills records and Part 1/Part 2 reports; hash checks accompany this step.
