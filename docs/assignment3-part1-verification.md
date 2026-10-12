# Assignment 3.1 — Verification evidence

Updated: October 12, 2026. Status: documentation consistency and existing
application regression checks passed. Student/submission review remains pending.

## Acceptance for this milestone

The documents must agree on the selected scope, distinguish proposals from
implemented behavior, map all R1–R4 and D1–D6 findings, cover the experience and
technical boundaries, identify actual inspected reuse candidates, include
truthful AI disclosure and curated evidence, and keep earlier report/code/data
files intact. Local document links must resolve. The report must identify
unresolved submission steps without pretending an old commit contains this work.

## Checks and observed results

- Earlier experience/technical documentation checks passed: relative links,
  required sections, all ten research mappings, timing calculation, draft status,
  formatting, and existing reuse-file paths.
- Final package check passed across ten documents and 29 local links, checking
  fenced-block balance, trailing whitespace, ten research mappings, one intact
  Course Macros section, and explicit pending submitted-commit status.
- git diff --check passed. Source-control changes are Markdown documentation
  only; the earlier report, application source, dependency declarations, CSVs,
  and prior evidence files were not edited.
- Existing backend pytest suite: 328 passed, two non-failing dependency
  deprecation warnings. No dependency change was made to address warnings.
- Existing frontend API-client suite: 38 passed. Both linters passed without
  auto-fix, and production build passed (28 modules). Build output remains
  ignored. These are travel-app regression checks, not validation of the
  proposed skills application.

Observed verification runtime identifiers: Python 3.14.7, pytest 9.1.1, and
Vite 8.2.2. Tests used the existing local dependencies; none were installed or
upgraded. No application server was started and no skills provider call was made.

No skills runtime test, provider call, browser inspection, SQLite migration,
exercise timing measurement, accessibility test, or clean-checkout skills run
has been performed. There is no skills implementation to exercise in Part 1.

## Repeatable review

Review the Assignment 3 links in README and follow every relative link.
Check all ten research rows in the experience design against the supplied table.
Read the model response boundary and confirm it matches application-owned timing
and resources. Confirm that proposed file names/endpoints are not represented
as existing code. Run git diff --check. For regression verification, use the
existing commands in [travel verification](verification.md), without auto-fix
or dependency installation.

Student review must also inspect the Mermaid flow in a supporting viewer, verify
report links after publication, and confirm the AI-use identifiers. Automated
text/link checks cannot establish diagram rendering, design usability, clinical
effectiveness, or public availability of an unpublished document.

## Final readiness review

The [requirement matrix and checkpoint steps](assignment3-part1-readiness.md)
cover every Part 1 requirement in the supplied assignment. The student-reported
GPT-6.1 Sol / medium identifier is now disclosed. Timing-start wording and the
one-skill scope were clarified. Standalone Canvas-report links must be converted
to absolute links after the checkpoint exists. This review remains documentation-
only, with no new runtime verification or commit/publish/upload action.

Final review check passed: eleven documents, 42 local links, all ten R/D
mappings, student-reported model disclosure, explicit pending report commit,
unchanged Git HEAD, and Markdown-only changes. git diff --check passed.
