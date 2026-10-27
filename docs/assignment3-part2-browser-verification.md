# Assignment 3 Part 2 — Vue browser verification

Date: October 22, 2026. Coursework, fictional inputs only. This is an implementation
step record, not a final Part 2 report or submission claim.

## Environment and method

Used the existing installed dependencies and normal Vite configuration at
127.0.0.1:5173 with the FastAPI entry point at 127.0.0.1:8000. A temporary runner
injected separate travel/skills SQLite files under /private/tmp/hudson-skills-ui/,
disabled credentials, and replaced advisor provider functions with functions that
raise if invoked. No provider or crisis service was contacted. A preliminary
frontend at 5174 omitted optional devtools; the measured run and final browser
checks used the ordinary 5173 configuration. Local listener startup required the
sandbox's permission override; no unrelated process was stopped.

Backend regression command used the existing environment with
`PYDANTIC_DISABLE_PLUGINS=__all__ PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests -q`.
Optional Pydantic plugin discovery was disabled in the test process to avoid
cloud-placeholder metadata reads; application dependencies were not changed.
405 tests passed with two existing deprecation warnings. In frontend/, `npm test`,
`npm run lint`, and `npm run build` passed: 63 tests, both project linters, and
42 transformed modules. No package install or upgrade occurred.

## Observed browser cases

| Case | Observed result |
| --- | --- |
| Start/pause/resume/stop | Local controls worked, paused remaining phase was retained, explicit Resume continued, Stop ended exercise. Ordered events saved. |
| Full normal run | Session d5fd2550-23ac-42b8-8716-98e81120f60a rendered all 12 ordered phase cues, completed six cycles, with no pauses/support. |
| Timing | DOM observation after Vue nextTick: 60,004 active ms. Engine: 60,000 ms. Setup: 9,345 ms. Saved completion revision 13, cycles 6, final exhale remaining 0. |
| Cold save timeout | UI showed Not saved; explicit Retry saving succeeded with the retained queue. No duplicate session created. |
| Backend unavailable | With backend stopped, started a new exercise; pacing and controls worked. Crisis dialog rendered bundled links/text. Leave returned immediately to idle. |
| Backend restored | Restarted same temporary backend/database; explicit Retry saved the queued session. History survived service restart and browser reload. |
| Reload/recovery | No automatic exercise restart. Reviewed unfinished record, explicitly marked interrupted; repeated after correction and verified list/detail agreed and marker cleared after reload. |
| Crisis keyboard behavior | Native dialog focused Back, Escape closed it and returned focus to Crisis support. Exercise remained paused; Resume was explicit. |
| Small screen/static | At 360×640, Crisis/Leave and fixed Pause/Stop remained in viewport. Static cue computed transform was none. Simpler view retained controls. |
| Navigation | Switching to Travel stopped exercise; returning showed Exercise stopped. Travel query survived view switching. |
| Travel regression | Harbor Lantern Hotel returned T001/T009, Boston MA, 9/18–9/20 and 10/2–10/4 at $150. Not a Real Hotel cleared stale results and disabled booking selection. No booking was written. |
| Console | Browser warning/error log returned no entries after final checks. |

The first interruption review exposed a stale history list row after successful
interruption: detail said interrupted while the row said running. Updated the row
from the response and cleared the recovery marker only after reconciliation.
Repeated browser testing confirmed the correction.

Travel SQLite SHA-256 before and after read-only searches was unchanged:
`758af3d584258d17163e08ff679f4955a61cae106f56b7fc0d0020443263cb83`.
Temporary skills integrity check returned ok; curated export contains eight
fictional sessions and 48 events. No development database or CSV was modified.

## Evidence

- [Completed exercise](../evidence/assignment3-part2-ui/completed-exercise.jpg)
- [Crisis panel while backend offline](../evidence/assignment3-part2-ui/crisis-backend-offline.jpg)
- [Leave despite save failure](../evidence/assignment3-part2-ui/leave-save-failure.jpg)
- [Mobile static simpler view](../evidence/assignment3-part2-ui/mobile-static.jpg)
- [Fictional temporary database records](../evidence/assignment3-part2-ui/session-records.json)
- [Reverified resource sources and limits](assignment3-part1-resources.md)

## Limits and next step

DOM cue observation is not hardware paint telemetry. The 60.004-second result is
one desktop run, not a timing guarantee across devices or evidence of clinical
effectiveness. API records remain client-reported with timing_verified false.
The actual operating-system reduced-motion preference, screen readers, full
keyboard accessibility, and external phone/SMS/chat handlers were not exercised;
reduced-motion logic is unit-tested and CSS-enforced, and static mode was observed.
No full offline frontend cache or cold offline startup is implemented.

Saving on pagehide is best-effort. A crash/reload can leave a running checkpoint;
explicit reconciliation records its last acknowledged duration, not unknown time.
Queues are in memory; closing a tab or choosing another exercise can lose unsent
events. Retry applies only while that queue remains available. A conflict is
surfaced rather than silently rewriting other-tab history. No continuous
monitoring, cross-tab coordination, or automatic clinical interpretation exists.

Optional mocked conversation/history and approved personalization remain to be
implemented. There is no live-model contribution or peer evaluation in this step.
No commit, push, upload, deployment, or submission was performed. All temporary
services created for this verification were stopped after testing.
