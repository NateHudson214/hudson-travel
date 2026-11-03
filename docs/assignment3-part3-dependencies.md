# Part 3 approved dependency updates — November 2, 2026

**Verified in isolation; repository lockfile updated.** Only four package records
changed, matching the student's exact approved versions. Package declarations,
production source, Python versions and original frontend node_modules are
unchanged. No major update or override was applied.

| Package | Previous lock | Verified lock |
| --- | --- | --- |
| Vite | 8.2.2 | 8.2.4 |
| shell-quote | 1.10.0 | 1.11.0 |
| source-map-js | 1.2.1 | 1.2.2 |
| brace-expansion | 5.0.9 | 5.0.12 |

## Isolated resolution and verification

Used the existing `/private/tmp/hudson-part3-setup-20261102` copy and its existing
Python environment. Exact temporary package constraints let npm resolve the four
versions in lock-only mode. The original package.json was restored, the lock
normalized against its original declarations, then `npm ci --ignore-scripts`
installed that lock only inside the temporary copy. Final root dependency entries
are identical; no extra direct dependency or override remains. Install scripts
were skipped; successful build/startup verified the installed toolchain needed
by this project. No audit fix/force or unapproved graph update occurred.

After verification, the byte-identical candidate lockfile was copied into
`frontend/package-lock.json`. The original frontend installation was not upgraded
and may still contain the old versions. To reproduce the verified lock later,
run `npm ci` in frontend only when a local install is intended/authorized.
The current task installed only inside the isolated folder.

- Full mock backend suite: **492 passed in 5.69 s**, unchanged Python environment.
- Frontend: **87 passed**, non-fixing Oxlint and ESLint passed; **Vite 8.2.4 build,
  53 modules**, passed.
- Normal README backend reload and frontend dev startup passed. Browser confirmed
  exact/lowercase/trimmed/partial Harbor Lantern searches (T001/T009, $150),
  unmatched and blank results clearing, simpler options, fixed mock conversation
  saving, Start/Pause/Resume/Stop/Leave, and support Back staying paused.
- An initial DOM checkbox locator found no match. A fresh AX observation and
  indexed toggle succeeded; no application failure is inferred from that
  automation mismatch. No new full-duration exercise timing is claimed.
- Isolated credentials were absent, mode mock, all saved turns mock, reservations
  zero, SQLite integrity/foreign keys valid. No external resource was contacted.

This remains an **unpublished copied-files snapshot**, with the previously
repaired tests and new lockfile. No committed clean checkout is claimed.

## Remaining ESLint/minimatch investigation

The verified install's read-only audit decreased from **11 package findings
(7 moderate, 3 high, 1 critical)** to **7 moderate, 0 high, 0 critical**. Remaining:
minimatch plus inherited findings in @eslint/config-array, eslint,
@eslint-community/eslint-utils, @eslint/js, eslint-plugin-vue and vue-eslint-parser.
All seven nodes are dev dependencies in this lock. This is not a claim that the
original older node_modules has already been remediated or that no other risk
exists. Audit exit 1 is expected while findings remain.

Current registry metadata lists minimatch 10 releases only through 10.2.6.
Latest ESLint 10.14.0 still requires minimatch ^10.2.6; latest config-array 0.23.5
requires ^10.2.4. The [reviewed advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249)
lists patched 11.0.1, outside those parent ranges. A routine compatible parent
update therefore has not been established as a fix. No minimatch major upgrade,
override, manual library patch or ancient solver-recommended downgrade was used.

The advisory's specific amplification requires attacker-controlled globs and
optimizationLevel >=2. Installed minimatch defaults to 1; inspected ESLint helpers
and config-array pass dot:true and do not set that option. The project uses fixed
repository globs, and skills messages never feed these lint tools. This supports
lower exposure in the inspected local lint paths; it is **not a patched package,
complete call-graph proof, exploit test or reason to erase the audit finding**.
No malicious pattern was executed.

Remaining choices: keep this as an explicit student-reviewed local-coursework
limitation for now, or separately authorize a coordinated supported lint-tool
remediation investigation. No acceptance is presumed. Testing minimatch 11 by
an override or another major tool change needs new scope and compatibility checks.
No additional update within the current parent ranges is claimed available.

## Preservation and evidence

Original database/.env/CSV/prior-report hashes and durable allowance remain
unchanged: eight/$0.80 reserved, two/$0.20 available. These are reservations,
not billing. Only test services/tab were closed. No live call, commit, push or
submission occurred. Recordings/code explanation, final readiness decisions and
an eventual exact committed checkout remain separate.

- [Results and limits](../evidence/assignment3-part3-dependencies/results.json)
- [Exact lock changes](../evidence/assignment3-part3-dependencies/lock-changes.json) and [verified hash](../evidence/assignment3-part3-dependencies/verified-lock.sha256)
- [Backend gate](../evidence/assignment3-part3-dependencies/backend-tests.txt), [frontend gate](../evidence/assignment3-part3-dependencies/frontend-checks.txt)
- [Audit after updates](../evidence/assignment3-part3-dependencies/npm-audit.json)
- [Lint registry metadata](../evidence/assignment3-part3-dependencies/lint-registry-metadata.json) and [installed-path review](../evidence/assignment3-part3-dependencies/remaining-lint-review.json)
- [Runtime mock/DB checks](../evidence/assignment3-part3-dependencies/runtime-safety.json)
- [Browser observations](../evidence/assignment3-part3-dependencies/browser-observations.json), [mock screen](../evidence/assignment3-part3-dependencies/mock-browser.jpg)
- [Isolated install](../evidence/assignment3-part3-dependencies/isolated-install.txt), [exact resolution](../evidence/assignment3-part3-dependencies/lock-resolution.txt), [normalization](../evidence/assignment3-part3-dependencies/lock-normalization.txt)
