# Assignment 3 Part 3 — Fictional evaluation matrix

Evaluated November 2, 2026. **All fifteen planned mock scenarios and B1–B3 passed
under the documented test conditions.** Fresh browser/SQLite observations and
local simulated contracts are distinguished below. This does not complete live
variation, clean-checkout verification or recording requirements.
Use only fictional messages and temporary records for destructive/race cases.
Record exact expected/observed behavior, mode, input/build fingerprint and evidence.

## Three explicit behavior checks

- **B1 — Independent safety and exit:** Crisis support and Leave remain reachable
  across exercise, simpler, waiting, failures, history and confirmation. Opening
  support pauses pacing; returning never resumes it. Never contact real services.
- **B2 — Application/user authority:** exactly six 4/6 cycles; model selects only
  compatible reviewed replies/facts. No arbitrary prose or model change to timing,
  navigation/preferences. History/reuse/Show more never start or resume breathing.
  Reduced motion overrides motion choices. Conversation is optional/outside pacing.
- **B3 — Durable, limited writes:** exact retries do not duplicate/redispatch;
  cancel/clear generations reject late writes. Reset and clear are distinct;
  history clearing cannot reset the live allowance. Restoring history dispatches
  no call; actual mode/status/measurement claims match saved records.

## Expected versus observed — completed mock/browser run

| ID | Fictional input or user action | Expected result | Checks | Observed / status |
| --- | --- | --- | --- | --- |
| S01 | Choose Simpler view while ready, then Show more | Optional conversation/history hide; safety/Start remain; Show more restores options without starting | B1 B2 | PASS — Browser: simpler ready hid conversation/history; Start/support/Leave remained; Show more restored options with engine still ready. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S02 | Stop or complete an exercise in Simpler view, then Show more | No optional chat entry until Show more; user remains stopped/completed | B1 B2 | PASS — Browser: both completed and stopped simpler views hid after-conversation; Show more restored it while the terminal state stayed unchanged. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S03 | Start and finish all six cycles without input | Twelve ordered cues, no chat call inside, actual guided interval <=90 s including delays; setup separate | B2 B3 | PASS — Fresh browser: 12 ordered cues/six cycles, 60005 ms DOM active, 60002 ms clock, 17146 ms setup; pause/support zero; no chat inside sequence. [Evidence](../evidence/assignment3-part3-evaluation/timing.json) |
| S04 | Pause midway through a phase, wait, explicitly Resume | Phase remainder retained; pause excluded; no restart or automatic continuation | B1 B2 | PASS — Browser pause froze active clock at 8267 ms and the same exhale remainder; final stopped record separates 8834 ms active from 17118 ms other pauses. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S05 | Open support during running/paused state, Back, then Resume | Local panel opens; Back remains paused; explicit Resume only | B1 B2 | PASS — Support opened from paused and running; both returns stayed paused. Saved support time 10233 ms was separate from other pauses. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S06 | Leave while running or waiting for a reply | Immediate idle; stopped/cancelled or safe late-result handling; no penalty | B1 B2 B3 | PASS — Active Leave saved stopped at 317 ms and reached idle. Pending-turn Leave/support/exit stayed responsive; delayed mock completed in storage while late UI result remained ignored. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S07 | Before: “Fictional character asks whether typing is required.” | Labeled mock approved exercise/no-typing reply; optional continuation and persisted pair | B1 B2 B3 | PASS — Before mock rendered exercise/no-typing/pause facts, saved the pair, and restored it after real backend restart. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S08 | After: “Fictional character dislikes moving cues.” | Labeled mock reviewed static-option fact; no automatic setting change; history persists | B1 B2 B3 | PASS — After mock rendered acknowledgment/static-display option, linked to the completed session, made no preference save, and restored from history. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S09 | Inject unknown reply ID/extra prose/malformed selection | Fixed application fallback; failed run; no rejected raw output saved/rendered; safety/Leave work | B1 B2 B3 | PASS — Browser malformed extra-prose fixture produced fixed fallback and usable safety/exit; four ASGI variants rejected unknown IDs, null output, incompatible facts and extra prose without saving raw rejected text. [Evidence](../evidence/assignment3-part3-evaluation/malformed-variants.json) |
| S10 | Load composer, stop only test backend, send fictional draft | Bounded error and retained draft; local support/Leave usable; no silent retry | B1 B3 | PASS — Backend genuinely stopped: Send retained draft/error and explicit Retry; local support/Leave worked. Unsent draft was absent from SQLite before clearing. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S11 | Save simpler/static, reload, Use last setup; test reduced motion | Load never applies/starts; reuse explicit; device reduced motion wins | B1 B2 B3 | PASS — Save/reload/reuse stayed explicit and ready. A test-only JavaScript matchMedia fixture forced staticCue=true/transform=none despite saved gentle motion; no actual OS toggle is claimed. [Evidence](../evidence/assignment3-part3-evaluation/browser-observations.json) |
| S12 | Reset display choices with existing history and a failed/in-flight preference write | Local display reset; saved choice reset retry explicit; sessions/conversations retained | B1 B2 B3 | PASS — Named temporary reset-write failure changed display locally and showed warning; explicit retry cleared saved choices, preserved 4 sessions/3 conversations. Injected async preference test serialized reset behind old save using revision 1. [Evidence](../evidence/assignment3-part3-evaluation/reset-storage.json) |
| S13 | Open Clear history, cancel; later confirm in temporary DB | Cancel preserves data; confirm clears sessions/chats, preserves preferences and allowance | B1 B3 | PASS — Cancel preserved all 5 sessions/3 conversations. Confirm cleared 33 events/8 messages/4 runs, kept preferences/ledger, epoch became 1. Old turn/session writes returned 409; a new epoch-1 mock conversation saved afterward. [Evidence](../evidence/assignment3-part3-evaluation/clear-verification.json) |
| S14 | Refresh/restart with unfinished session and saved conversation | No auto-resume; acknowledged lower-bound checkpoint/history restored; explicit reconcile only | B1 B2 B3 | PASS — Real backend restart restored paused 283 ms checkpoint without resuming. Explicit reconciliation changed only status to interrupted; completed timing and saved conversations restored without a model call. [Evidence](../evidence/assignment3-part3-evaluation/restart-outage.json) |
| S15 | Duplicate pending Send; cancel/clear while fake provider waits; return late result | One dispatch; durable cancellation/epoch check; no recreated records or refunded allowance | B1 B2 B3 | PASS — Two local MockTransport dispatches: duplicates returned pending without redispatch; cancellation stayed cancelled; clear rejected late result/retry with 409, preserved preferences and two nonrefunded fake reservations. [Evidence](../evidence/assignment3-part3-evaluation/backend-races.json) |

## Method, fresh measurements and verification

Expected outcomes were preserved [before the run](../evidence/assignment3-part3-evaluation/expected.json).
The [results summary](../evidence/assignment3-part3-evaluation/results.json),
[complete browser observations](../evidence/assignment3-part3-evaluation/browser-observations.json),
[source fingerprint](../evidence/assignment3-part3-evaluation/source-manifest.json)
and [timestamped local requests](../evidence/assignment3-part3-evaluation/requests.jsonl)
identify this actual uncommitted Part 3 build. This is new observation evidence,
not a claim that test totals substitute for scenarios. Earlier step/Part 2 evidence
remains background. The evaluation made no application-source change.

The actual app ran with temporary skills/travel databases, absent credentials,
mock mode and forbidden real provider dispatch. Named fixtures supplied malformed
output and a two-second local mock delay. Storage reset failure used an explicitly
named temporary SQLite trigger, removed before the user chose Retry. Backend
outage/restart cases actually stopped/restarted only the evaluation backend.
A recoverable temporary fixture backup and curated records were saved before
history deletion; original user databases were never cleared or modified.

The fresh static-cue run measured **60.005 s DOM-observed active, 60.002 s clock,
17.146 s setup**, twelve ordered cues and six cycles. Pause/support were both zero;
SQLite/request timestamps show no conversation request within the sequence.
No response is required after Start. Setup starts when the ready engine/view is
created and includes chosen setup actions; cold navigation/asset loading is not
included. This is one observed sample including completion/render delay, not
hardware-paint telemetry, exact per-phase jitter validation or a device-wide
performance/clinical guarantee. Values were not clamped to the planned 60 seconds.
See [timing JSON](../evidence/assignment3-part3-evaluation/timing.json) and
[completed screen](../evidence/assignment3-part3-evaluation/completed-timing.jpg).

S04 froze at 8.267 active seconds while paused; its final stopped record separates
8.834 active, 17.118 other-pause and 10.233 support seconds. S14 restored exactly
the acknowledged 283 ms lower-bound checkpoint and changed status only on explicit
reconciliation; no exact crash-lost duration is inferred. Original records were
exported [before temporary clear](../evidence/assignment3-part3-evaluation/records-before-clear.json).
The clear removed five sessions/33 events/three conversations/eight messages/four
mock runs, preserved preferences/allowance, and advanced generation to 1. Old
writes returned 409; a later new generation-1 conversation correctly saved.
[Post-clear activity](../evidence/assignment3-part3-evaluation/postclear-new-activity.json)
therefore is intentional new history, not deleted-record resurrection.

S11 used an explicitly test-only JavaScript `matchMedia` fixture reporting reduced
motion. The real compiled component produced staticCue=true/transform=none despite
a saved gentle choice. This did not toggle the OS or emulate all CSS media behavior.
S12 additionally exercised the actual preference controller with injected local
promises: Reset applied locally before an older save finished, then used fresh
revision 1 to persist the reset; no real HTTP call. [Race details](../evidence/assignment3-part3-evaluation/preference-race.json).
S15 used actual ASGI routes, a fake key and `httpx.MockTransport` in a different
temporary DB. Its existing lifecycle schema labels those simulated runs live, but
**two fake transport dispatches are not real provider calls** and cannot be used
as live-model evidence. The original environment/ledger stayed mocked/unchanged.

The three behavior checks passed across the exercised conditions: B1 safety/exit
through ready, pacing, paused, pending, rejected response, storage failure, actual
backend outage, history and clear confirmation; B2 fixed pacing/allowed text,
explicit reuse/start/resume and simulated reduced-motion precedence; B3 exact
pending retries, cancelled/cleared late results, preserved preference/allowance,
restart/history reads and actual mode/timing metadata. No crisis service was contacted.

Final regressions passed **492 backend tests, 87 frontend tests, non-fixing
oxlint/ESLint and the 53-module production build**, with two existing backend
deprecation warnings. Existing dependencies were reused; none was installed.
Original skills/travel DB and Part 1/Part 2 report hashes match the pre-run values.
At the end of this mock-only run the original allowance was four reserved attempts/$0.40, leaving six/$0.60;
those reservations are not billed-cost measurements. The evaluation tab/services
were closed. No commit, push or submission occurred.

## Repeated live variation — authorized batch executed

The [separate four-attempt live batch](assignment3-part3-live-checks.md) repeated
typing twice and motion twice. Typing 1 timed out (3066 ms) and saved the fixed
fallback; typing 2 completed the expected selection (1522 ms). Both motion
selections were identical and expected (2693/1838 ms). No retry or fifth dispatch.
This is three successful selections and one availability failure, not four passes.
There are not two successful typing selections to compare. The original ledger
is now 8/$0.80 reserved, leaving 2/$0.20. Mock mode restored; source unchanged.
See the linked method/evidence for pricing, usage and persistence verification.

## Surprising finding, decision and untested limits

An immediate Leave can coexist with a **completed saved mock turn**: the delayed
S06 request was still processing when the UI reached idle, then its pair was saved.
The late reply never returned to the abandoned view. This counterintuitive result
is consistent with best-effort cancellation; it does not show that Leave undid a
server write. Decision: retain immediate local exit, late-result guards and accurate
saved-message wording rather than promising cancellation of already dispatched
work. S15 separately verifies actual pending-run cancellation and clear-generation
rejection with local simulated transport. Do not present either as a paid failure.

The compact simpler-view display controls remain an explicit D1/D3 versus D5/R4
tradeoff, not a patient research result. Untested limits still include actual
OS preference toggling/CSS media integration, screen-reader/full accessibility,
hardware paint/per-phase jitter across devices/load, and cold offline frontend
startup. The provisional 250 ms cue-delay threshold has not been empirically
validated. Keep these limits even though the planned mocked cases passed.
