# Assignment 3 Part 2 — Evidence and submission checklist

Final review: October 27, 2026. Student approval and checkpoint/publication
authorization received; 492 backend/85 frontend, lint/build passed again.
This source checklist is not proof of a remote publication or Canvas submission.
At the review stage, no commit/publication had occurred. Checkpoint publication
is authorized separately; no merge, visibility change or Canvas action is authorized.
Live mode remains mock. No further model call is needed to finish this milestone.

## Review decision before checkpoint

Read the [final readiness review](assignment3-part2-readiness.md) and
[report draft](../assignment3/part2/report.md). Accept the disclosed Part 2 scope
or request a separate refinement step before publishing:

- Simpler view retains optional conversation and Save/Reset controls, unlike the
  original sketch's stronger contraction.
- History labels reply origin/fallback but does not display exact run-status
  badges despite the live cancellation copy mentioning saved statuses.
- Setup excludes cold page load; the existing measured DOM sample does not
  establish per-phase jitter/device-wide timing. The 250 ms threshold is provisional.
- Live sends were four one-off headless checks. Actual saved replies were later
  verified in browser history without new calls. No live browser Send, full
  accessibility/OS-motion audit or clean-checkout result is claimed.

These are documented limits to approve/refine, not silent changes to the approved
Part 1 proposal. Part 3's larger evaluation/recordings remain separate.

## Evidence inventory to include in the reviewed checkpoint

| Required claim | Evidence to review / include | Status |
| --- | --- | --- |
| Chosen skill, flow, research rationale, boundaries | [Plan](assignment3-part1-plan.md), [experience](assignment3-part1-experience.md), [technical](assignment3-part1-technical.md), [resources](assignment3-part1-resources.md); final report/review | Present; preserve the earlier Part 1 report. |
| Complete skill and duration | evidence/assignment3-part2-readiness/timing.json, completed-current-build.jpg, records.json; browser verification guide | Earlier observed sample: DOM 60.011 s / clock 60.010 s; setup 12.055 s, twelve cues/six cycles. |
| Actual model/context contribution | docs/assignment3-part2-live-checks.md; evidence/assignment3-part2-live-checks/batch.json, verification.json | Four real OpenAI gpt-6-luna calls, four expected selections, no retries. |
| Sessions/conversations/history | Session/conversation guides, restart records/screenshots, final-review/live-history.jpg | Persistent records and actual live history UI verified. |
| Failure, support and Leave | Final-review fallback.jpg, offline-error.jpg, offline-support.jpg, mock-records.json; earlier failure evidence | Mock invalid response and real local backend outage verified. |
| Preferences and separate confirmed clear | Preference/clear guides and evidence folders; temporary-database tests | Verified with mocks; allowance survives clear. |
| Lifecycle/allowance/response restrictions | Adapter guide, backend/tests/skills/test_live.py, frontend tests, source fingerprint | Current tested source; no further paid fault injection. |
| AI-use and revised/failed approach | AI-USE.md and evidence/assignment3-part2-log.md | Curated disclosures, lost timing capture/query-contract correction documented. |
| Final no-call review | docs/assignment3-part2-readiness.md and evidence/assignment3-part2-final-review/ | Added without app source/data changes or new calls. |
| Submitted version and accessible pinned links | Real checkpoint SHA and post-publication upload-ready report.md | PENDING. |
| Recording relevant to this milestone | None currently | Part 2 implementation paragraph does not explicitly require a video; add one if instructor directs/chosen. Part 3 recordings remain required. |

Do not relabel the older Assignment 2 video as Assignment 3 evidence. Do not
upload a full chat export, raw provider output, secrets, SQLite files or
research-participant/private third-party material. These evidence files contain
fictional cases/application-rendered replies and curated technical metadata.

## Exact authorized-checkpoint sequence — not executed here

1. Student approves the review draft and the limits above (or asks for fixes).
2. Authorize work on the existing `codex/assignment3-part2-foundations` branch.
   Do not reuse the Part 1 HEAD as the Part 2 submitted commit. Preserve earlier
   work and any unrelated local changes; do not reset the checkout.
3. Recheck mock mode and ledger: exactly four reservations/$0.40 currently,
   six/$0.60 remaining, no new live calls. Keep the original ignored skills DB
   to retain this allowance; history clearing does not reset it.
4. Run the documentation/link/whitespace checks and normal mock checkpoint gates:
   full backend pytest suite, frontend tests, non-fixing lint and production
   build. Current unchanged source last passed 492 backend/85 frontend tests.
   If source changes during finalization, verify those changes before committing.
5. Review the complete staged/untracked diff and stage **only** reviewed Assignment
   3 work: app integration and skills modules/tests, preserved TravelView extraction,
   frontend skills/API/tests and test-discovery script, `.env.example`, README,
   AGENTS, AI-USE, Assignment 3 design/step/final docs, Part 2 report and curated
   Assignment 3 evidence. Include only relevant reviewed resource-note changes.
   Exclude .env, credentials, backend/instance databases, temporary harnesses,
   .venv, node_modules, dist, caches and unrelated changes. Course CSVs stay unchanged.
6. Commit the reviewed Part 2 milestone and publish that branch to origin only.
   Record the actual resulting full commit SHA. Do not merge or change visibility.
7. After that checkpoint exists remotely, generate a **separate upload-ready
   report.md** containing its exact SHA and absolute commit-pinned design/evidence
   links. Keep assignment3/part2/report.md as the checkpoint's draft if necessary;
   generating the external upload copy afterward avoids a self-referential commit.
   Do not pretend a report containing PENDING/local links is the final upload.
8. Check every pinned link against the actual remote commit, not a moving branch.
   A link has the form
   `https://github.com/NateHudson214/hudson-travel/blob/<REAL_PART2_SHA>/<path>`.
   This is a template, not an existing link or a verified commit. Confirm source,
   design, report/evidence and image links resolve to the checkpoint's contents.
9. Verify grader access. If the repository is intended public, test pinned links
   without relying on your signed-in GitHub session. If private, confirm the
   instructor/grader has the required access. Do not infer access from your own
   account or change visibility automatically. Check any recording permissions
   separately if a recording is added.

## Exact remaining manual Canvas actions

Only after the authorized checkpoint/pinned upload file and access checks:

1. Open [Assignment 3.2 — Part 2 Submission](https://psu.instructure.com/courses/2484533/assignments/18506999).
2. Confirm the course, assignment name and currently displayed submission/due
   information. This review did not inspect Canvas state or assume a deadline.
3. Choose the file-upload submission option and select the **separate finalized
   report.md** delivered after checkpoint publication. Do not select Part 1's
   report or this current PENDING/local-link draft.
4. Check the filename/preview and required Canvas fields. Submit it yourself.
5. Confirm the submission receipt/time and uploaded report.md. Open/download the
   submitted file and spot-check its real Part 2 SHA and pinned evidence links.

Nothing in this checklist is authorization to submit on the student's behalf.

## Exact next prompt if accepting the documented limits

> I approve the final Assignment 3 Part 2 report and documented scope limits,
> including the simpler-view and history-status differences. On the existing
> codex/assignment3-part2-foundations branch, run the mock-only checkpoint checks,
> commit only the reviewed Part 2 implementation, documentation and curated
> evidence, and publish the branch to origin. Keep mock mode enabled and make no
> live calls. Generate a separate upload-ready report.md with the exact checkpoint
> commit and absolute commit-pinned evidence links. Do not merge, change repository
> visibility or submit to Canvas. Give me the upload file and exact remaining
> manual access-verification/submission steps.

If the limits are not acceptable, request the specific refinement instead of
sending this approval prompt. Existing live allowance is not permission for more
calls; they require a new explicit authorization.
