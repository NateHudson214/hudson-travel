# Assignment 3.1 — Final readiness review

Reviewed October 12, 2026 against the assignment text and R/D table supplied by
the student. Verdict: **Part 1 design content is ready for student review and
checkpointing; the report is not ready to upload yet.** No grade or instructor
acceptance is implied. No commit, push, merge, or upload was performed.

Checkpoint authorization update: the student subsequently reviewed and approved
the design and authorized branch creation, documentation checks, commit, branch
publication, and a standalone upload report. These instructions remain useful
as a process record; actual checkpoint identity is recorded in the separate
upload copy after Git creates it. No merge, visibility change, or Canvas upload
is authorized in this step.

## Requirements review

| Part 1 requirement | Evidence | Review result |
| --- | --- | --- |
| Choose one or more supplied skills and preserve its steps | [Experience](assignment3-part1-experience.md) | Covered: six 4/6 breathing cycles; optional before/after conversation. |
| Sketch or flow of the main experience | Experience Mermaid flow, text sketch, and view table | Covered as design artifacts. Mermaid rendering still needs visual review; a structural sketch is present independently. |
| Connect important decisions to R1–R4/D1–D6 | Experience research table; [plan](assignment3-part1-plan.md) source table | All ten mapped with reasoning, alternatives, and costs. Counts are not effectiveness claims. |
| Balance personalization, user control, and effort | Experience/technical preference and simpler-view sections | Explicit choices, no automatic distress inference or preference setting; no mandatory emotional disclosure. |
| Model contribution and limits | [Technical design](assignment3-part1-technical.md) | Contextual selection of approved replies/facts; application renders content and controls state. Limited expression/intent misreading acknowledged. |
| Relevant context and saved conversation/session records | Technical records/context/API sections | Proposed SQLite records, bounded context, versions, and history restoration. No implemented storage claimed. |
| Review history and explain saved information | Technical history/deletion sections | Proposed visible history, explicit reset/clear controls, mock/live status, and limits of local storage. |
| Exercise within 90 seconds at intended pace | Experience/technical timing sections | 60-second target, first actionable instruction to completion, delays included, setup/pause/support separated. No measured duration claimed. |
| Crisis route available throughout and independent of model | Global controls and [resource notes](assignment3-part1-resources.md) | Proposed bundled panel; available during errors. Source-backed U.S. contacts; device/network behavior untested. |
| Deliberate crisis-input decision and its limits | Technical crisis section | No clinical detector or routing; model signpost may miss input and never gates resources. |
| Familiar stack and reviewable organization | Technical architecture/reuse and README | Same Vue/FastAPI stack, separate skills view/database, application-owned queries. |
| Identify reuse | Technical inspected-file table | Concrete planned adaptations; hotel-specific SQL/prompt/data excluded. No completed code reuse claimed. |
| Useful README/AGENTS/design notes and open questions | README, AGENTS, linked design files | Covered; later engineering questions remain explicit. No new setup/dependencies required for Part 1. |
| Coursework role and fictional evaluation boundary | All principal design documents, report, AGENTS | Explicit; no diagnosis, therapy, monitoring, or offering as support. |
| AI disclosure and curated evidence including revision/failure | [AI-USE](../AI-USE.md), [log](../evidence/assignment3-part1-log.md) | Model now recorded as GPT-6.1 Sol, medium effort. Genuine reply-boundary revision and failed source fetch recorded. No fabricated runtime evidence. |
| One report with repository, submitted commit, accessible evidence | [Report draft](../assignment3/part1/report.md) | Repository and document inventory present. Exact checkpoint and absolute accessible upload links remain pending. |

Existing regression results are 328 backend tests and 38 frontend tests passed,
both linters passed, and build passed. These were run during preparation and
are documented in [verification](assignment3-part1-verification.md); they do not
validate skills behavior. Only documentation changed during this review, so
runtime checks were not repeated without a new source change or failure.

## Corrections made in this review

- Record the student's GPT-6.1 Sol / medium disclosure, rather than substituting
  a pre-existing hotel-provider model. Desktop version remains unavailable.
- Remove the plan's suggestion of a change-to-another-skill control: only one
  skill is in scope, while declining/leaving remain real options.
- Make the Ready screen a setup overview, with the first actionable guided
  instruction after Start. All delays/instructions after that boundary count
  toward the measured exercise duration.
- Explain that Canvas cannot resolve repository-relative links in a standalone
  report. The upload copy must use accessible absolute links.

## Remaining gaps by milestone

**Before upload:** student reviews the documents and sketch/flow; create and
publish an approved documentation checkpoint; create the upload report with its
exact commit and accessible absolute evidence links; verify reviewer access.
Desktop version can be added if available; it is honestly marked unavailable
and is not a requirement to invent or a reason to block the design milestone.

**Implementation questions, not missing Part 1 runtime evidence:** final reply
catalog wording, provider schema support/model configuration, emergency-resource
copy/source review, clock jitter, interruption/persistence recovery, race handling,
and durable live-test budgets. The model contribution is narrower than open-ended
chat, but no requirement for freely generated prose appears in the supplied
instructions. Ask the instructor only if their additional rubric requires it.

**Later milestones:** working interface, measured duration, SQLite persistence,
independent resource access under failure, accessibility/browser checks, fifteen
fictional scenarios and three explicit behavior checks, mock/live variation,
surprising finding, untested limitation, recordings, and clean-checkout run.
Their absence is stated honestly and does not justify implementing them during
this documentation-only request.

## Exact checkpoint and submission sequence

1. Read the report and linked design documents. Preview the experience file in
   a Mermaid-capable Markdown viewer and inspect its text sketch. Check pause,
   stop, failure, history, and crisis-access behavior. Supply corrections if any;
   do not state review is complete until it is.
2. When satisfied, authorize the documentation checkpoint with the exact prompt
   below. Proposed branch: codex/assignment3-part1-design. Stage only the reviewed
   Markdown files, inspect the staged diff, and run documentation checks. Reuse
   existing runtime results unless a source change or failure requires rerunning.
   Do not install dependencies, modify application code, or include ignored data.
3. Commit the approved documentation with the message "Document Assignment 3
   Part 1 skills prototype design" and record the actual full commit hash. Publish
   that branch to the existing origin only after the student authorizes it. No
   main-branch merge is necessary to make commit-pinned design links reviewable.
4. After the hash exists, generate a **separate upload copy named report.md**
   outside the committed draft (for example, /private/tmp/assignment3-part1-upload/report.md).
   Put the checkpoint hash and repository URL in it, remove draft/pending
   publication statements as appropriate, and replace each local evidence link
   with an absolute GitHub blob link pinned to that hash. This avoids pretending
   a commit can contain its own future hash. The uploaded report describes the
   committed design checkpoint; the repository keeps the design/report source.
5. Open the commit link and every report evidence link in a browser with the
   permissions a grader will have. Confirm the files render and the diagram is
   readable. If the repository is private, grant the required course reviewer
   access through GitHub or ask the instructor for their accepted access method.
   Do not change repository visibility automatically.
6. Open [Assignment 3.1 — Part 1 submission](https://psu.instructure.com/courses/2484533/assignments/18506998),
   using the link supplied in the assignment. Read the current upload directions,
   choose the finalized standalone report.md, submit it, then verify the uploaded
   filename and submission receipt/status. Canvas has not been inspected here;
   exact button labels, due date, and accepted file options must be read there.
   Do not upload the old root report.md or this still-pending repository draft.

The checkpoint prompt to send **after completing document review** is:

> I reviewed and approve the Assignment 3 Part 1 design documents. Create the
> codex/assignment3-part1-design branch, run the documentation checkpoint checks,
> commit only the reviewed documentation, and publish that branch to origin.
> Generate a separate upload-ready report.md with the exact checkpoint commit
> and absolute commit-pinned evidence links. Do not merge, change repository
> visibility, modify application code, or submit to Canvas. Give me the upload
> file and exact remaining manual verification/submission steps.

All checkpoint and submission actions above are instructions for a future
authorized step. This review performed none of them.
