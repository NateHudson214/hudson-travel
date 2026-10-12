# Assignment 3.1 — Part 1 plan

Updated: October 12, 2026.

Status: requirements review and scope selection complete. The student selected
60-second paced breathing with optional conversation before/after the exercise.
The [experience design](assignment3-part1-experience.md) is drafted for review.
The [technical design](assignment3-part1-technical.md) specifies proposed records,
model boundaries, timing, failure handling, and reuse candidates.
The student confirmed a separate view in this repository, its own database,
U.S. resource scope, and constrained model replies. The
[report draft](../assignment3/part1/report.md) and supporting guidance are prepared.
Part 1 is a design milestone, not a working application milestone.

## Assignment boundary

Design a localhost coursework skills prototype using Vue, FastAPI, and SQLite.
Use only fictional scenarios. The prototype must not diagnose, claim to provide
therapy, imply monitoring, or be offered as a tool to rely on during distress.

Part 1 needs an explainable, implementable design: chosen skill(s), a sketch or
flow diagram, model responsibilities and limits, planned stored information,
history review, personalization and user control, research reasoning and
tradeoffs, and unresolved questions. Keep README, AGENTS.md, and design notes
useful for subsequent implementation.

The running skill, model integration, SQLite persistence, and measured duration
are Part 2 implementation work. Final refinement, fifteen fictional scenarios,
three explicit behavior checks, live-model variation checks, demonstration,
failure/process recording, and clean-checkout verification belong to Part 3.
Plan for these requirements now without reporting them as completed.

Each milestone requires its own report.md with repository URL, submitted commit,
accessible design/evidence links, completion status, and unresolved items. The
final repository needs AI-USE.md. Maintain curated, redacted evidence throughout,
including a failed or revised approach; do not fabricate failures for evidence.

## Selected starting scope

Implement one skill first: paced breathing with a four-second inhale and a
six-second exhale. Use six cycles (60 seconds). Application-owned text and
pacing carry the exercise; optional model conversation occurs before or after
it. No typing or model response is required to start or complete the exercise.

Timing starts at the first exercise instruction and ends at the final planned
step. Account for transition and completion delays within the 90-second limit.
The 60-second figure is a design target, not a measured implementation result.
Report entry/setup time separately. Exclude user-chosen pauses and crisis-resource
access from active exercise timing; do not impose a forced exit at a deadline.

Propose a restrained pacing cue with a text/count alternative and reduced-motion
support. Keep Stop/Leave and clearly identified Crisis support available in
every screen and failure state. Choosing to stop carries no penalty.

Offer an explicit simpler-view control rather than inferring distress from text.
Keep remembered choices optional and editable, with a way to decline breathing
or reset preferences. No other skill is offered in the initial scope. Do not
present saved history as evidence of clinical
improvement.

Why start here: breathing provides a bounded, measurable sequence with little
reading, typing, or disclosure (R1, D2, D3). A subtle or static cue addresses D6.
Tradeoff: one skill limits choice (R4), so the design must allow declining the
exercise and leaving; adding another skill later remains an open scope decision.
Grounding is a possible alternative. Cognitive reframing adds more reading and
disclosure, making D3 harder to satisfy in the first implementation.

## Research source supplied by the student

The assignment describes 15 patients, 13 clinicians, 15 prototype evaluation
sessions, and 150 participant–task combinations. Counts indicate occurrences
of coded findings, not clinical effectiveness or distinct participants unless
explicitly stated. This table summarizes the student's supplied R/D material.

| ID | Finding | Reported evidence |
| --- | --- | --- |
| R1 | Skills beyond 90–100 seconds lose attention; about 60 seconds was comfortable. | 38 mentions, concentrated on shorter exercises and paced breathing. |
| R2 | Crisis access must be frictionless, without navigation through screens. | 30 mentions across all 15 participants, on crisis access and the overall journey. |
| R3 | Users need permission to stop or leave without consequence or cost. | 39 mentions; all 15 participants raised it on the permission-to-stop task. |
| R4 | Users control their journey and receive options rather than automatic routing. | 68 mentions, strongest on stopping, journey, and choosing by emotional state. |
| D1 | Progressive interface contraction: less content as distress rises. Detection and what contracts were not established. | 54 mentions, heaviest on crisis access and the overall journey. |
| D2 | One atomic skill/action at a time. | 100 mentions across all 15 participants, concentrated on STOP, reframing, and breathing. |
| D3 | Minimize emotional cost: demands to feel, disclose, or perform. | 148 mentions, present for every participant, concentrated on breathing and grounding. |
| D4 | Safety remains persistently visible, including inside an exercise. | 31 mentions, almost entirely on crisis access and the overall journey. |
| D5 | Personalization without configuration burden, using prior actions and lightweight feedback. | 49 mentions, heaviest on feedback and choosing by emotional state. |
| D6 | Low-stimulus, non-judgmental language; avoid diagnostic or condescending phrasing and demanding color/motion. | 97 mentions across all 15 participants, heaviest on reframing and the overall journey. |

## Step sequence and acceptance checks

1. Requirements review (complete): distinguish Part 1 from implementation and
   final evaluation; obtain the full R/D table; identify proposed scope.
2. Scope decision (complete): student selects skill(s) and confirms the model's optional
   role. Record alternatives, benefits, and costs rather than just feature lists.
3. Experience design (drafted for review): create a flow/sketch covering entry, selection, exercise,
   stop/pause, completion, history, model failure, and independent crisis access.
   Map important decisions to R/D findings and explain conflicting priorities.
4. Technical design (drafted for review): specify application/model boundaries, approved skill
   context, SQLite records, history visibility, personalization/reset behavior,
   failure handling, timing measurement, and proposed code organization.
5. Documentation and evidence (drafted for review): update README and AGENTS.md appropriately; start
   a truthful AI-use disclosure and curated evidence log; identify actual reuse
   versus new code. Prepare the Part 1 report and unresolved questions.
6. Student review and submission checkpoint: verify documentation links and
   consistency, record the submitted commit and accessible links, and provide
   exact manual submission actions. Do not mark a draft as submission-ready.

## Remaining review items

- Review the proposed record/clear-history behavior and constrained reply catalog.
- Drafting model is recorded as student-reported GPT-6.1 Sol, medium effort;
  desktop version remains unavailable and can be added if visible.
- Review emergency-resource wording and rendered diagram before submission.
- Commit/publish the reviewed milestone and record its exact submission links.

## Evidence for this step

The student supplied the assignment instructions and then the missing R/D table.
The coding assistant read AGENTS.md, README.md, existing design/verification
notes, and the current handoff. The repository was clean at the initial check.
This step adds planning documentation only. No application behavior, database,
dependency, or credential was changed; no model request or browser test was run.
The student then selected 60-second paced breathing and optional before/after
conversation. The assistant drafted the experience flow, structural sketch,
all ten R/D mappings, tradeoffs, controls, and proposed review scenarios in
assignment3-part1-experience.md. These are not observed runtime results.
The assistant then inspected the existing application read-only and drafted the
technical design. The student confirmed the flagged organization, U.S. resource
region, and constrained model contribution. Guidance, AI disclosure, curated
evidence, resource notes, and report are now drafted. Student review, disclosure
review, submission checkpoint/publication, and upload remain unfinished. The
student supplied the AI drafting model/effort and requested a final documentation
readiness review; see [the review and submission steps](assignment3-part1-readiness.md).
