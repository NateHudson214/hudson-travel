# Assignment 3.1 — Part 1 report draft

Status: student-reviewed documentation milestone; repository report source for
the standalone upload copy. Updated October 12, 2026.

Repository: [NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel).

**Submitted version commit: PENDING.** These documents are not committed or
published yet. The existing baseline is
1e6bc9d93f63b3bcc1f41053f0dcf21daeb0544a; it does not contain this milestone.
Do not use that baseline as the submitted version. Once reviewed and committed,
record the actual milestone commit and convert the links below to accessible
repository links pinned to that commit. Do not invent a hash or claim publication.

## Design and rationale

The proposed Skills Prototype is a separate view in this repository, with a
separate SQLite database. It supports six cycles of four-second inhale and
six-second exhale, targeting 60 active seconds. Optional model conversation
occurs before or after. No reading checkpoint, typing, or provider delay is
required during the exercise. The active timing target remains to be measured.

R1 motivates the short sequence. R2/D4 motivate persistent, independently
rendered U.S. crisis information. R3/R4 motivate immediate stop/leave and explicit
choice. D1 becomes user-selected simpler view because the study establishes no
reliable distress detection. D2/D3 motivate one current cue and no required
disclosure. D5 motivates remembered explicit display choices without onboarding
questions. D6 motivates restrained motion and neutral language. One skill limits
choice and constrained replies limit expression; those tradeoffs are documented
rather than claimed away.

The model selects approved neutral reply/fact IDs using reviewed skill context,
limited conversation history, and relevant explicit preferences. Application
code will render approved text and own timing, state, persistence, navigation,
and crisis access. This bounds invented advice but does not prove correct intent
interpretation. No clinical detector, diagnosis, therapy, or monitoring is claimed.

Proposed persistence includes fictional sessions/events, conversations/messages,
model-run status/version records, and explicit display preferences. History
restoration requires no new model call. Reuse candidates include existing
credential-loading, HTTP/error, temporary-database, bounded-history, and short-
transaction patterns; hotel prompts, SQL generation, maps, and data are excluded.
No reuse is implemented at this milestone.

## Design documents and evidence

These relative links work in the local repository. They will be reviewable on
GitHub only after the milestone is published and permissions allow access.

- [Requirements and selected scope](../../docs/assignment3-part1-plan.md)
- [Experience flow, sketch, and complete research rationale](../../docs/assignment3-part1-experience.md)
- [Technical records, model boundaries, timing, failures, and reuse](../../docs/assignment3-part1-technical.md)
- [U.S. resources and source-verification limits](../../docs/assignment3-part1-resources.md)
- [Verification evidence and untested behavior](../../docs/assignment3-part1-verification.md)
- [Curated redacted prompt/decision/revision log](../../evidence/assignment3-part1-log.md)
- [AI-use disclosure draft](../../AI-USE.md)
- [Project README](../../README.md) and [agent guidance](../../AGENTS.md)

The revised approach replaces potentially open-ended replies with constrained
reply/fact selection. An actual source-fetch failure and its resulting decision
are also recorded. These are design/process evidence, not a fabricated runtime
test. No recording is supplied or claimed for Part 1; finished demonstration and
failure/process recordings are planned for the later milestone.

## Complete and unresolved

Complete as drafts: selected scope, experience flow/sketch, all ten R/D mappings
and tradeoffs, technical proposal, planned reuse, README/AGENTS guidance, resource
source notes, curated evidence, AI disclosure, and this report. See the linked
verification note for actual check results.

Drafting AI: GPT-6.1 Sol with medium reasoning effort, reported by the student;
desktop app version unavailable. See AI-USE.md for tools and roles.

The student reviewed and approved the Part 1 design on October 12, 2026.

Unresolved implementation questions: emergency-resource
copy review, diagram rendering review, and instructor confirmation if more
open-ended model generation is expected. Implementation must resolve provider
schema support, clock-jitter tolerance, crash/persistence recovery, race handling,
and durable live-test budgets. None of the proposed skills runtime behavior,
90-second acceptance, accessibility, model quality, or clean-checkout operation
has been verified. The study counts are design evidence, not effectiveness.

Submission steps still required:
commit and publish the approved version, put its exact hash and accessible
commit-pinned links in the report, check those links as a reviewer, and manually
upload this report.md to the Assignment 3.1 Canvas submission. No commit, push,
or upload was performed while preparing this draft.

The [readiness review and exact checkpoint/submission sequence](../../docs/assignment3-part1-readiness.md)
explain how to make a standalone upload report with absolute, commit-pinned
links. Relative links in this repository draft must not be used unchanged in a
Canvas upload, where they have no repository directory to resolve against.

All future tests/demonstrations use fictional scenarios. This coursework
prototype must not be offered, deployed, or recommended as mental-health support.
