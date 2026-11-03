# Part 3 fixture repair and dependency triage — November 2, 2026

**Backend blocker resolved without dependency changes.** The existing isolated
install now passes all **492 backend tests**. Dependency findings are triaged,
not fixed; any update remains a separate approval decision. This is still an
unpublished snapshot, not a committed clean checkout.

Later authorized follow-up: [four compatible updates are verified and locked](assignment3-part3-dependencies.md). The audit is now seven moderate findings; the
pre-update table and decisions below preserve this earlier review. Remaining
lint-chain remediation/limitation is still unresolved.

## Test-only repair and verification

Changed 29 state patches in five skills test files from attribute patching to
`monkeypatch.setitem(app.state._state, name, value)`. Starlette State stores its
dynamic settings in that dictionary. Patching the actual mapping lets pytest
restore its previous entries during teardown, including repeated overrides.
Tests deliberately depend on State's internal storage; future State changes must
be reverified. Production state/routes, timing, model boundary, database schemas,
travel code and dependency versions are unchanged.

The first correction converted 28 single-line calls: 444 passed/48 errors exposed
one remaining multiline clock-provider patch. Converting it resolved all errors;
[first-run output](../evidence/assignment3-part3-compatibility/first-correction-tests.txt)
is retained, not hidden. No production workaround, library modification, skipped
test or dependency downgrade was used.

Only the five corrected files were copied to the existing isolated folder.
No environment was recreated and no dependency installed. Results:

- Isolated README backend command: **492 passed in 5.39 s**, pytest 9.2.0.
- Original environment's relevant skills suite: **164 passed**, two existing
  dependency deprecation warnings.
- Separate isolated in-process skills suite: **164 passed** and every original
  app-state key/binding was preserved after pytest returned. Its one assertion-
  rewrite warning concerns an already imported anyio module in that diagnostic.
- Frontend source/lock/dependencies are unchanged; the prior isolated **87 tests,
  two non-fixing linters and build** remain applicable. They were not rerun or
  presented as new results. No UI behavior changed, so no new browser run.

## Audit scope and all eleven flagged packages

Read-only `npm audit --json` confirms 7 moderate, 3 high, 1 critical **package
findings**. These are not eleven independent bugs: five packages have direct
advisories (twelve unique advisory IDs) and six inherit an ESLint dependency
finding. The command's exit 1 reports findings, not an installation failure.
No audit fix/force, npm update, installation, exploit payload or upgrade was run.
Registry metadata checks only confirmed candidate versions/ranges. Source and
installed dependency paths were inspected without executing a vulnerability.

| Flagged package, installed version | Severity / dependency path | Local exposure assessment / approval candidate |
| --- | --- | --- |
| shell-quote 1.10.0 | Critical; npm-run-all2 -> shell-quote, dev | Advisory concerns command quoting with a comment token followed by an attacker-controlled line terminator. Current lint scripts are fixed repository strings; no skills message flows into this Node tool. npm-run-all2 does use quote/parse, so do not dismiss its presence. Candidate **1.11.0**, within parent ^1.8.4. |
| source-map-js 1.2.1 | High; Vue compiler and Vite -> PostCSS | Marked production in the lock via Vue, so it cannot be classified as entirely dev-only. Indexed source-map consumption can block the event loop. Current app has no user source-map/compile upload interface; exposure is inferred lower for this fixed-source build, not proven unreachable. Candidate **1.2.2**, within observed parent ^1.2.1. |
| brace-expansion 5.0.9 | High; ESLint -> minimatch | Three CPU/stack denial-of-service advisories concern malicious brace patterns. Present in lint tooling, not the FastAPI skills request path. Trusted repository globs reduce current input exposure, not package severity. Candidate **5.0.12**, within parent ^5.0.8, covers all three reported ranges. |
| minimatch 10.2.6 | Moderate; ESLint and @eslint/config-array | Malicious glob amplification; patched **11.0.1** is a major update outside both parent ^10 ranges. Requires separate compatibility review/approval; no forced override. |
| vite 8.2.2 | High aggregate; direct dev dependency | Six advisories: editor launch/flags, Windows escaping/existence checks, cross-origin custom middleware, non-Windows allowed-path bypass and four-byte wasm query disclosure. Windows-only conditions do not match this Mac, but other server paths may. Loopback is not proof of immunity. Candidate **8.2.4**, within declared ^8.1.5 and compatible with Node 24.20.0. |
| @eslint/config-array 0.23.5 | Moderate inherited via minimatch | Same lint/glob input boundary; requires compatible minimatch remediation. |
| eslint 10.9.1 | Moderate inherited via minimatch/config-array/utils | Same chain, not a separate reported application flaw. |
| @eslint-community/eslint-utils 4.10.1 | Moderate inherited via eslint | Same chain / peer relationship. |
| @eslint/js 10.0.1 | Moderate inherited via eslint | Same chain. |
| eslint-plugin-vue 10.9.2 | Moderate inherited via eslint/utils/parser | Same chain. |
| vue-eslint-parser 10.4.1 | Moderate inherited via eslint | Same chain. |

The npm solver suggests ancient major downgrades (including ESLint 4) for parts
of the inherited chain. They are not an acceptable automatic fix for the current
ESLint 10 configuration. Read-only registry lookup found latest ESLint 10.14.0
still depends on minimatch ^10.2.6 and latest config-array 0.23.5 on ^10.2.4;
updating ESLint alone therefore does not establish remediation. Do not claim
zero findings from the proposed four updates: they have not been installed or
audited after changing, and the minimatch chain would still need resolution.

## Primary advisory sources checked

- [shell-quote quoting injection; patched 1.11.0](https://github.com/advisories/GHSA-pqg4-j6r4-53mv)
- [source-map-js indexed-map denial of service; patched 1.2.2](https://github.com/advisories/GHSA-68fv-2mgg-jv7q)
- [minimatch amplification; patched 11.0.1](https://github.com/advisories/GHSA-g3hv-75wg-m249)
- brace-expansion: [quadratic expansion](https://github.com/advisories/GHSA-q2hr-2g5m-vwhr), [nested braces](https://github.com/advisories/GHSA-qhr7-859c-m2p7), [comma recursion](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p)
- Vite: [Windows escaping](https://github.com/advisories/GHSA-698v-4r3x-3vcv), [editor flags and patched Vite 8.2.4](https://github.com/advisories/GHSA-r825-w8mm-5pxw), [Windows existence check](https://github.com/advisories/GHSA-587h-7wmj-h5pm), [cross-origin middleware](https://github.com/advisories/GHSA-9jrq-w75r-8gcw), [allowed-path bypass](https://github.com/advisories/GHSA-rq7h-c2jc-7f22), [wasm disclosure](https://github.com/advisories/GHSA-vfpm-58rq-9qcg)

Input-path assessment above is an inference from installed/source inspection,
not a penetration test or proof that every reported issue is exploitable here.

## Decisions needing student input

1. Approve testing compatible updates **Vite 8.2.4, shell-quote 1.11.0,
   source-map-js 1.2.2 and brace-expansion 5.0.12** in isolation, followed by
   reviewed lockfile changes and full verification. Shell-quote is a minor
   update; the other three are patch updates. None has been applied.
2. Separately approve investigation of a supported ESLint/minimatch remediation
   if desired. A major minimatch override, coordinated lint-tool change, direct
   dependency addition or downgrade is outside this repair. Alternatively record
   a student-reviewed temporary limitation for trusted local coursework; no
   acceptance has been presumed. No backend version change is necessary for
   the fixture fix. Python requirements remain unpinned as a reproducibility limit.

Original database/.env/CSV/prior-report hashes and allowance are unchanged:
eight/$0.80 reserved, two/$0.20 remain. No real provider call, installation,
commit, push or submission. No service needed restarting. Final committed
checkout, recordings/code explanation and publication remain pending.

Evidence: [results](../evidence/assignment3-part3-compatibility/results.json),
[changed test fingerprints](../evidence/assignment3-part3-compatibility/changed-tests.json),
[isolated full suite](../evidence/assignment3-part3-compatibility/isolated-backend-tests.txt),
[original skills suite](../evidence/assignment3-part3-compatibility/existing-skills-tests.txt),
[state restoration check](../evidence/assignment3-part3-compatibility/state-isolation-tests.txt),
[raw npm advisory report](../evidence/assignment3-part3-compatibility/npm-audit.json),
[installed paths](../evidence/assignment3-part3-compatibility/npm-paths.json).
