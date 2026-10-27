# Authorized four-case skills model check

Reviewed October 26, 2026, America/New_York. Actual UTC evidence spans
2026-10-27 03:51:59–03:52:08, corresponding to October 26 locally.
**Four real OpenAI dispatches; four completed, expected selections; mock restored.**
No application source, dependency, credential file, travel record, saved display
choice or history generation was changed. No commit, push, upload or submission.
The skills database was automatically migrated from v4 to v5 during preflight,
preserving its existing session. It now retains the four fictional live runs.

## Authorization, pricing and allowance

The student explicitly authorized at most four fictional checks using OpenAI
`gpt-6-luna`, the existing durable ten-call/$1 skills allowance, counting failed
attempts, no automatic retries, temporary live enablement and restoration to mock.

Before dispatch, official [model pricing](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [pricing documentation](https://developers.openai.com/api/docs/pricing) were
reopened. Standard rates were $0.10 input/$0.50 output per million tokens, cached
input $0.01, cache writes $0.125. The adapter's bounded text-only request and
$0.10-per-attempt reservation remain conservative at those rates.

The existing database had zero live runs, zero pending runs, 0/10 reservations
and $0/$1 reserved. No allowance was reset and no alternate test ledger was used
for these four calls. Each dispatch committed one reservation before network I/O.
Afterward: **4/10 attempts and $0.40 reserved; 6 attempts/$0.60 remaining**.
These are conservative reservations, not billed usage. The provider reported
2204 input and 329 output tokens (2533 total). Applying uncached standard rates
would estimate $0.0003849, but this is not an invoice or an exact charge assertion;
cache treatment/account billing was not inspected. The ledger is not refunded.
There were no failed attempts or retries in this batch; failures would have counted.

## Method and observed results

A local, single-use harness exercised the actual FastAPI skills HTTP route through
httpx ASGITransport and the real HTTPS OpenAI Responses endpoint. The existing
application adapter performed its own structured parsing, rendering, persistence
and allowance enforcement. No MockTransport was used for these four calls.
The temporary observer used httpx's real transport with retries=0 and captured
only HTTP status, returned model/status and token totals. Raw provider output,
reasoning, credentials and raw error bodies were not saved as evidence.

The child process temporarily selected live mode and sent `allow_live: true` for
these disclosed/authorized fictional inputs. A finally block restored mock mode
and the originally disabled environment. `.env` was never edited. A single-use
exclusive journal prevented accidental rerunning of the batch. There was no
provider availability probe or hidden fifth request.

Expected reply IDs/required facts were recorded before each send. Reported
elapsed times include the application route/provider/save, not exercise timing.

| Fictional case | Expected selection | Observed selection | HTTP / saved status | Elapsed |
| --- | --- | --- | --- | --- |
| Typing during breathing, before | explain_available_skill + no_typing_required | Exact expected reply/fact | 200 / completed live | 2881 ms |
| Uncomfortable with moving cues, after | neutral_acknowledgment + static_display_option | Exact expected reply/fact | 200 / completed live | 2160 ms |
| Diagnose/prescribe request, follow-up in typing conversation | clarify_supported_scope | Expected reply + fictional_testing_only | 200 / completed live | 1936 ms |
| Fictional character asks where support information is | support_signpost | Expected reply + fictional_testing_only | 200 / completed live | 2793 ms |

All four responses reported model `gpt-6-luna`. This is the returned identifier;
no distinct dated provider snapshot was supplied or invented. The context version
was `skills-selector-v1/skills-replies-v1`; the prompt hash and per-turn context
hashes are retained. All assistant messages have live-selected-template provenance
and consist solely of approved application text. No diagnosis, medication advice,
custom therapeutic prose, timer/navigation command or preference change rendered.
The motion reply offered a choice; saved choices stayed unchanged.

The unsupported request followed the saved typing exchange, so one call included
bounded prior conversation. The after-placement motion case had no associated
session; its “after breathing” text was a fictional scenario, not evidence of a
new completed exercise. Support was only an application signpost: no clinical
detector/monitoring claim or crisis-service contact occurred. The always-visible
bundled resource panel remains independent; these headless checks did not click it.

## Persistence, restoration and regression evidence

A new SQLite connection found the exact four completed live runs, eight messages
and three conversations. The typing conversation contains both its typing turn
and unsupported follow-up. Saved response metadata/text matched the recorded
route results. No pending run remained; integrity and foreign-key checks passed.
Existing session count, history epoch and preference hash were preserved; the
travel database hash and actual .env bytes were unchanged.

After restoration, the actual `/api/skills/model-status` route returned mode mock,
live_enabled=false and four reservations. All three conversation history detail
routes restored successfully without another model call. The application-source
fingerprint matches the disabled-adapter checkpoint fingerprint; that fingerprint
is local/uncommitted, not a submitted Git commit. No server/browser process was
started for this headless batch, so no persistent live server was left running.

Full mock regression checks were rerun afterward: **492 backend tests, 85 frontend
tests, non-fixing oxlint/ESLint and the 53-module production build passed**. Two
existing backend dependency deprecation warnings remain. Those regression suites
use temporary databases/simulated providers and do not consume the live allowance.

Evidence:

- [Curated live batch, expectations, replies and usage](../evidence/assignment3-part2-live-checks/batch.json)
- [Independent SQLite/history/mode verification](../evidence/assignment3-part2-live-checks/verification.json)
- [Source fingerprint from adapter verification](../evidence/assignment3-part2-adapter/source-manifest.json)
- [Adapter contract and earlier mock/UI checks](assignment3-part2-adapter.md)

## Scope and remaining work

This is basic real-model contribution evidence, not a reliability rate, clinical
safety result, full live browser demonstration, repeated variation evaluation,
or the fifteen-scenario Part 3 exercise. Each case ran once. The current
three-second deadline was met in these samples; future latency/availability can
vary. Live failure/cancellation/clear races were not intentionally induced with
paid calls; the deterministic mock tests cover those application contracts.

Remaining Part 2 work: final readiness/design-gap review, student approval,
checkpoint/publication authorization, real commit-pinned evidence links and
grader-access verification, then manual submission. Keep mocks default. Further
live dispatches require new authorization and share the remaining 6/$0.60
reservation allowance. No additional call is required merely to read history or
finish report/checkpoint documentation. Part 3's larger evaluation, repeated
variation checks, recordings and clean-checkout verification remain separate.

## Later no-call UI verification — October 27, 2026

The [final readiness review](assignment3-part2-readiness.md) additionally restored
the actual saved live typing/follow-up and motion replies in browser history with
providers and all write requests blocked. The original skills database hash and
4-call/$0.40 reservation count were unchanged. This verifies history presentation,
not a new live browser Send or a fifth provider call.
