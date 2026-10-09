# Hudson Travel — Part 2 Report Draft

**Assignment:** Part 2 SQLite Booking CRUD

**Due:** Tuesday, September 15, 2026, at 11:59 PM ET

**Repository URL:** [https://github.com/NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel)

**Preserved Part 1 implementation/evidence checkpoint:**
[`d224428019dd6fb7223c4e607aabc108af145577`](https://github.com/NateHudson214/hudson-travel/commit/d224428019dd6fb7223c4e607aabc108af145577)

**Exact Part 2 implementation checkpoint:**
[`2a127bf79e8cb66069b0c1a9695391a8e2924507`](https://github.com/NateHudson214/hudson-travel/commit/2a127bf79e8cb66069b0c1a9695391a8e2924507)

**Exact Part 2 merge checkpoint:**
[`95635eff2dc77fdf4f6e9dd5b842a62a239e1f3f`](https://github.com/NateHudson214/hudson-travel/commit/95635eff2dc77fdf4f6e9dd5b842a62a239e1f3f)

## Project context

Hudson Travel is a local educational application built with Vue, FastAPI, and
SQLite. Part 1's hotel-name search is preserved. Part 2 seeds the supplied
hotel, trip, user, and booking records into SQLite once, then performs all
search and booking reads and writes through FastAPI. The bookings are simulated;
the application does not make real reservations or process payments.

## Responsibilities

### Interface

Vue preserves hotel-name search and loads travelers plus joined booking history
when the page starts. A user searches for a hotel, selects a traveler and one
displayed offered trip, and creates a booking. The history table shows booking
ID, traveler, trip, hotel, stay dates, booked-on date, and status. Confirmed
bookings can be cancelled while remaining visible, and a test booking can be
deleted. Clear loading, validation, success, error, and empty states are shown.
Booking and search errors do not erase valid state from the other workflow.

### Logic

FastAPI exposes hotel search, traveler and joined-history reads, booking
creation, cancellation, and deletion. Python validates references, assigns the
booking date and initial `confirmed` status, and allocates monotonic `B` IDs in
an immediate transaction. Vue sends every CRUD operation to FastAPI and rereads
history after create, cancel, and delete so the database remains the source of
truth.

### Data

On first initialization, Python reads all four supplied CSV files with
`utf-8-sig`, creates the relational schema, preserves every supplied ID, stores
a durable `csv_seed_version` marker, and initializes `next_booking_number` in
one transaction. Every later application read and write uses
`backend/instance/hudson_travel.sqlite3`; the ignored development database is
not committed. Foreign keys are enabled for every connection. The marker—not
row counts or individual records—prevents deleted starter records from being
restored and prevents duplicate seeding.

## API behavior

| Operation | Contract | Result |
| --- | --- | --- |
| Search | `GET /api/trips?hotel_name={name}` | SQLite-backed matching offered stays |
| Read travelers | `GET /api/users` | Supplied travelers for the selector |
| Read history | `GET /api/bookings` | Joined booking, user, trip, and hotel rows |
| Create | `POST /api/bookings` with `user_id`, `trip_id` | `201`, backend ID/date, `confirmed` row |
| Cancel | `PATCH /api/bookings/{id}` with `{"status":"cancelled"}` | Retained joined row with cancelled status |
| Delete | `DELETE /api/bookings/{id}` | `204`; row removed |

## Expected versus observed verification

| Check | Expected | Observed |
| --- | --- | --- |
| Backend tests | One-time seed, preserved IDs/counts, SQLite search, persistent CRUD, non-reused IDs, clear errors | 15 passed; two non-failing framework dependency warnings |
| Frontend API-client tests | User/history reads, exact create/cancel/delete requests, useful error handling | 11 passed |
| Frontend lint/build | No lint findings and a successful production bundle | Oxlint and ESLint passed; Vite transformed 18 modules |
| Protected files | All CSV and dependency-declaration hashes unchanged | Passed after implementation |
| Database exclusion | Local SQLite state is ignored and untracked | Passed; `backend/instance/` is ignored |
| Browser CRUD | Create, read, cancel-retain, and delete all initiated through Vue | Passed: B007 created and cancelled-retained; B008 created and deleted; service logs recorded GET/POST/PATCH/DELETE |
| Browser refresh | Saved changes remain after refreshing the page | Passed: B007 persisted and B008 remained absent |
| Service restart | Changes persist, deletions stay deleted, seed records do not duplicate/reappear | Passed: seven rows after restart—B001–B006 plus cancelled B007; B008 absent; counter 9 |
| Browser failure isolation and console | Clear errors, unrelated state retained, no healthy-console errors | Passed: failed create showed a clear error, retained two search rows and seven history rows, recovered through Refresh history, and healthy console was clean |
| Manual VS Code scan | Only intentional files; no secrets/generated output/CSV edits | Passed September 14, 2026; student confirmed every visible change was intentional and protected/generated files were excluded |

## Evidence and remaining work

The backend tests use temporary databases. The authorized browser smoke test
created the ignored development database and left it with the six seed bookings
plus cancelled B007; B008 remains deleted. The test passed in zero correction
cycles, including browser refresh, full service restart, controlled failure,
recovery, and console checks. Its detailed evidence is in
[`docs/verification.md`](docs/verification.md). The final manual VS Code review
also passed: the student confirmed every visible change was intentional, no
secrets or `.env` files were present, generated dependencies, build output, and
the ignored database were excluded, and all CSV and dependency declarations
were unmodified.

Substantial Part 2 work was committed on `part2-sqlite-bookings` at the exact
implementation checkpoint above and pushed as a remote feature branch. It was
then merged into `main` with a non-fast-forward merge. The complete automated
gate passed again on the combined `main`, and the merge plus final documentation
state were pushed to the public repository. Part 1 remains preserved in the
same history. This report is ready for the student's final Canvas upload.

Major implementation instructions are retained in
[`prompts/002-part2-sqlite-bookings.md`](prompts/002-part2-sqlite-bookings.md).

## Assignment 2 public API ZIP-lookup addendum

**Assignment:** A First Public API Request — graded ZIP extension

**Due:** Thursday, September 24, 2026, at 4:00 PM ET

The guided fixed button calls `/api/demo/zip-location`. The graded extension
accepts a five-digit ZIP as text, preserves leading zeros, calls
`/api/zip-location?zip_code={zip_code}` through FastAPI, and displays postcode,
locality, country code, latitude, and longitude in a plain Vue table. The API
key stays in the Python backend. Geoapify hotel retrieval, maps, Leaflet,
shortlists, and later assignment behavior remain outside this activity.

### Expected versus observed ZIP verification

| Check | Expected | Observed September 23, 2026 |
| --- | --- | --- |
| Automated gate | ZIP route/client coverage plus clean regressions | 19 focused and 57 total backend tests passed with two non-failing dependency warnings; 17 frontend tests, both linters, and the 20-module build passed |
| Live entered ZIP | `16802` returns a usable U.S. location | Passed: State College, `us`, `40.803167822`, `-77.861384958` |
| Browser request | Vue calls only the local FastAPI route and receives no key | Backend recorded `GET /api/zip-location?zip_code=16802` with HTTP 200; no key appeared in the path or rendered response |
| Loading | Loading feedback appears and conflicting ZIP controls disable | Passed with a delayed local-only response |
| Leading zero | `02113` remains five characters | Passed through a local-only response and the Vue table |
| Invalid input | Blank, short, long, letters, punctuation, and Unicode digits show validation, make no intentional request, and clear stale results | Passed for every listed value |
| Safe failures | Unresolved and provider failure show clear feedback | Local-only 404 and 502 checks passed and removed stale tables |
| Regression | Hotel search remains usable | `Harbor Lantern Hotel` returned T001 and T009 |
| Console | No healthy application warnings or errors | Passed |

One successful 16802 request was unintentionally repeated when the automation
tool's first field-clear action did not change the input. Later, unexpected
local requests for ZIPs 18042–18050 were observed from browser activity outside
the scripted smoke-test inputs, so the test backend was stopped immediately.
No credential or full provider URL was exposed. No source correction cycle was
needed.

### Request trace

`ZipLookupDemo.vue` handles the entered value and display state;
`frontend/src/api/location.js` builds the local request; `frontend/vite.config.js`
proxies `/api`; `backend/app/main.py` validates and maps the route response;
`backend/app/geoapify.py` sends and validates the provider request; and
`backend/app/config.py` reads the backend-only setting. The sanitized response
then returns through FastAPI and the Vite proxy to the Vue table.

### Earlier entered-ZIP activity evidence

These optional placeholders belong to the earlier standalone ZIP activity, not
the completed Assignment 2 Part 1 hotel-list-and-map evidence documented below.

- `evidence/assignment2-entered-zip-success.png` — **placeholder until the
  student saves and reviews it**
- `evidence/assignment2-entered-zip-validation.png` — **placeholder until the
  student saves and reviews it**
- Short screen recording of entered ZIP 16802, the result table, and the local
  Network request — **placeholder until recorded and reviewed**

The screenshot-ready success table was recreated through a one-request
local-only mock using the exact previously observed live response. That
recreated state is for visual capture and is not claimed as an additional live
provider verification.

## Assignment 2 Part 1 — live hotel search and map

**Repository:** [https://github.com/NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel)

**Assessed implementation and evidence checkpoint:**
[`0f38ae0ac35808e332ec91472bb0d5393e5adfc8`](https://github.com/NateHudson214/hudson-travel/commit/0f38ae0ac35808e332ec91472bb0d5393e5adfc8)

**Non-fast-forward merge checkpoint:**
[`6739c4e5b4e4a93b74d6558253078024b1aa7cbf`](https://github.com/NateHudson214/hudson-travel/commit/6739c4e5b4e4a93b74d6558253078024b1aa7cbf)

### Submission links

- **Startup and backend-only configuration:**
  [`README.md`](README.md#backend-setup)
- **Research notes and source decisions:**
  [`docs/assignment2-part1-research.md`](docs/assignment2-part1-research.md)
- **Early mockup:**
  [`docs/mockups/assignment2-part1-early.svg`](docs/mockups/assignment2-part1-early.svg)
- **Screen-recorded demonstration:**
  [`evidence/assignment2-part1-demo.mov`](evidence/assignment2-part1-demo.mov)
- **Detailed verification record:**
  [`docs/verification.md`](docs/verification.md#observed-nearby-hotel-smoke-test--september-29-2026)

The early mockup established the ZIP form, resolved center, list/map layout,
shared selection, attribution, and explicit invalid, unresolved, empty, and
service-failure states before implementation. The completed interface retained
those decisions, used a scrollable provider-results list beside the Leaflet
map, and preserved the earlier fixed and entered-ZIP workflows plus Assignment
1 behavior.

The authoritative Part 1 extension resolves a validated five-digit U.S. ZIP,
uses the returned coordinates as the center of a Geoapify Places search for up
to 20 `accommodation.hotel` results within 5,000 metres, and presents the
provider-derived results in a connected Vue list and Leaflet map. The API key
remains in the backend. Missing names, addresses, and distances are handled
honestly; the interface does not invent prices, ratings, availability, rooms,
or booking claims. Persistent shortlist behavior remains outside Part 1.

### Expected versus observed Part 1 verification

| Check | Expected | Observed September 29, 2026 |
| --- | --- | --- |
| Automated gate | Backend, frontend, lint, build, documentation, integrity, and ignore checks pass | 95 backend and 23 frontend tests passed; both linters and the 25-module build passed; protected checksums and ignore coverage passed |
| Live search | One Vue search for `16802` returns the resolved center and live nearby hotels | Passed: State College, `us`, `40.803167822`, `-77.861384958`, 5,000 metres, limit 20, and 20 hotels |
| Local request boundary | Vue calls only the local FastAPI route and exposes no credential | Backend recorded one HTTP 200 request to `/api/hotels/nearby?zip_code=16802`; no key or provider URL appeared in the rendered workflow or console |
| List and map | The same returned hotels appear as list items and markers | Passed: 20 list buttons and 20 numbered hotel markers were rendered |
| Selection | List and marker choices identify the same hotel | Passed for Hotel State College from the list and Hyatt Place State College from the map, including matching popup and `aria-current="true"` list selection |
| Honest data and attribution | Missing data is not invented; provider and tile attribution are visible | Passed: honest local-only missing-field fallbacks; Geoapify, Leaflet, and OpenStreetMap attribution visible; no commercial hotel claims |
| Browser states | Loading, invalid, empty, unresolved, and provider-failure states are clear and clear stale results | Passed using local-only mocks and all required invalid inputs; no additional provider request |
| Regressions | Existing workflows remain intact and no booking changes occur | Fixed/entered ZIP controls remained present; Harbor Lantern Hotel returned T001/T009; eight booking rows loaded; no mutation performed |
| Console and corrections | Healthy console is clean and defects are corrected | No warnings or errors; zero correction cycles |

The temporary local mock was stopped and removed, and the normal backend was
restored for evidence capture. The student then captured and reviewed all four
evidence files, confirming that they are readable, show the required live,
selection, attribution, and validation behavior, and contain no API key,
secret, private information, or unrelated content. The retained services were
stopped afterward and both application ports were released:

- [`evidence/assignment2-part1-live-hotels.png`](evidence/assignment2-part1-live-hotels.png) — reviewed live-results PNG
- [`evidence/assignment2-part1-selection.png`](evidence/assignment2-part1-selection.png) — reviewed synchronized-selection PNG
- [`evidence/assignment2-part1-states.png`](evidence/assignment2-part1-states.png) — reviewed validation-state PNG
- [`evidence/assignment2-part1-demo.mov`](evidence/assignment2-part1-demo.mov) — reviewed demonstration recording

### AI disclosure and evidence log

OpenAI Codex, a GPT-5-based coding agent, was used to inspect the existing Vue,
FastAPI, and SQLite architecture; research official Geoapify and Leaflet
documentation; prepare the early repository-native mockup; implement the
backend controllers and routes; implement the Vue list and Leaflet map; add and
run tests; perform bounded browser verification; and prepare documentation and
Git checkpoint evidence. The student supplied the authoritative requirements,
approved the exact Leaflet dependency addition, created and retained the local
Geoapify credential, performed the final VS Code review, and captured and
reviewed the submission evidence.

Selected prompt excerpts and their relationship to research, dependency
decisions, implementation, verification, and revised approaches are recorded in
[`prompts/003-assignment2-part1-live-hotels.md`](prompts/003-assignment2-part1-live-hotels.md).
The evidence log includes the decision to keep the provider key backend-only,
the explicit Leaflet approval, the 5 km/20-result Places contract, synchronized
selection requirements, the one-live-search smoke-test boundary, and the
revised manual capture approach when browser tooling could not safely preserve
all required live screenshots and video automatically.

### Checkpoint and submission status

Substantial Part 1 work is preserved on the published
`assignment2-part1-live-hotels` feature branch at the assessed checkpoint above.
It was merged into `main` with a non-fast-forward merge after the final VS Code
review and successful feature-branch gate. The complete gate passed again on
merged `main`, and the merge plus final documentation state are published.
Assignment 1 checkpoints remain in history. The remaining student action is to
upload this `report.md` to the Assignment 2 Part 1 Canvas submission and include
the repository, assessed commit, early mockup, and reviewed recording links or
files as the Canvas form permits.

## Assignment 2 Part 2 — local hotel in-class workflow

**Implementation and evidence checkpoint:**
[`77ae9b397caf3a3062d1ae8955aaf30cd0d1456d`](https://github.com/NateHudson214/hudson-travel/commit/77ae9b397caf3a3062d1ae8955aaf30cd0d1456d)

**Non-fast-forward merge checkpoint:**
[`79e0b6ddd0acb1909059ef344d1bc369f78fe25e`](https://github.com/NateHudson214/hudson-travel/commit/79e0b6ddd0acb1909059ef344d1bc369f78fe25e)

The `assignment2_part2_in_class` work adds separate SQLite storage
for Geoapify provider hotels without changing the instructor-supplied hotel,
trip, user, or booking records. A unique provider hotel/ZIP association retains
the resolved location context. Saving also creates five clearly labeled
simulated classroom nights for October 10–14, 2026. Repeated saves preserve
existing night values, and removing a provider hotel transactionally removes
only its associations and demo nights.

Vue now checks saved hotels before the live provider. Saved matches are labeled
**Saved locally**, display the simulated dates/rates/rooms, retain synchronized
list and Leaflet selection, and do not trigger a Geoapify request. An empty
successful local lookup falls through to the existing live endpoint, labeled
**API results**. Add and Remove controls update only after FastAPI confirms the
SQLite mutation.

### Expected versus observed in-class verification

| Check | Expected | Observed October 1, 2026 |
| --- | --- | --- |
| Automated gate | Database/API/client tests, lint, build, integrity, and ignore checks pass | 123 backend and 29 frontend tests passed; both linters and the 26-module build passed; protected hashes and ignore coverage passed |
| Live fallback | Empty local ZIP results fall through once to the provider | ZIP 16802 requested local storage first, then one live request returned 20 API results |
| Save | Two frontend saves create associations and five nights each | Both POST requests returned HTTP 201; counts became 2 hotels, 2 associations, and 10 nights |
| Local-first refresh | Saved matches display without a provider request | Two saved results, disclosures, map/list, and dated rows displayed; no live route appeared in backend logs |
| Edited classroom data | A DB Browser edit appears and persists | Hotel State College on October 12 displayed `$125.50` and 7 rooms before and after full service restart |
| Remove | Removing one hotel preserves unrelated data | Scholar Hotel State College returned HTTP 204 and stayed absent; Hotel State College and its five nights remained |
| Accessibility | List and map share one keyboard-accessible selection | One correction connected Leaflet marker keypress events; both directions then updated `aria-current` and the popup |
| Regressions | Earlier ZIP, hotel, booking, attribution, and console behavior remains healthy | ZIP controls remained, Harbor Lantern returned T001/T009, eight bookings remained untouched, attribution was visible, and the console was clean |

The retained development database now contains one saved provider hotel, one
ZIP association, and five demo-night rows. This local ignored database state is
verification data, not a repository artifact. Git checkpointing, submission
evidence packaging, and publication are complete; the required student
submission remains.

The student captured and reviewed the Part 2 submission evidence on October 5,
2026. `evidence/assignment2-part2-edited-rate.png` shows the saved-local Hotel
State College result with the edited October 12 `$125.50` rate and 7 rooms.
`evidence/assignment2-part2-local-first.png` shows the saved-local result and the
local saved-hotels Network request without a nearby-provider request.
`evidence/assignment2-part2-database.png` shows exactly five persisted nights
for Hotel State College, including the edited `12550`/7 values. The student
confirmed that the captures are readable and contain no API key, secret,
private information, or unrelated content. The retained Hudson Travel services
were stopped and ports 8000 and 5173 were confirmed free.

The final manual VS Code review passed on October 5, 2026. The student confirmed
that every visible change was intentional; the three evidence screenshots were
correct and readable; no `.env` file, API key, credential, generated dependency,
build output, cache, ignored SQLite database, editor setting, or unrelated file
was included; and all supplied CSV files and protected dependency declarations
remained unchanged. The reviewed implementation was approved for the bounded
Git checkpoint and merge process.

The reviewed work was committed and published on the
`assignment2_part2_in_class` feature branch at the implementation and evidence
checkpoint above. It was then merged into `main` with a non-fast-forward merge.
The full gate passed both before the feature commit and on merged `main`: 123
backend tests with the same two non-failing dependency warnings, 29 frontend
API-client tests, Oxlint, ESLint, the 26-module Vite production build,
dependency consistency, documentation links, whitespace, protected hashes,
evidence hashes, and ignore checks. No live Geoapify request occurred during
either Git gate. The feature branch, merge, and final documentation state are
published at [the Hudson Travel repository](https://github.com/NateHudson214/hudson-travel).

## Assignment 2 Part 2 — RAG hotel advisor draft

**Status as of October 8, 2026:** implementation, automated verification, and a
bounded visible-browser test using deterministic local-only provider mocks are
complete on `assignment2-part2-rag-chatbot`. A controlled live OpenAI workflow
also completed both model stages and local retrieval, but returned a grounded
no-match because the model chose 2024 for the yearless October question instead
of the stored 2026 demonstration dates. The prompt and regression tests now
require 2026 for yearless October ranges. A single corrected-year live run used
2026 and retrieved records, but its checkout boundary and reported total were
incorrect, so corrected submission evidence remains pending.

The next mocked-only correction removes both failure modes without changing the
public endpoint. The prompt defines October 12 as the excluded checkout boundary
for the required question. Total-cost retrieval exposes an integer
`total_cost_cents`; the provider returns the exact integer and a marker, and the
backend verifies the value before formatting dollars by dividing by 100. Tests
prove that two 10000-cent nights render as `$200.00` and reject shifted or
free-form dollar amounts. No further live request or evidence is claimed yet.

One subsequent authorized live attempt submitted the required question once
but stopped after the proposal stage. The local validator returned HTTP 422 and
persisted safe `unsafe_query` audit evidence as `C000004`, `M000008`, and
`R000006`; there is no assistant message. Retrieval and the grounded-answer
stage did not run, and no retry or success screenshot is claimed.

A read-only diagnostic later confirmed that the rejected proposal contained a
compound `UNION` and three joins. Both exceed deliberate validator limits, so
the validator was not loosened. The repository prompt now requires the graded
demonstration to use one flat `SELECT` with exactly two joins across the three
approved saved-hotel tables. Mocked integration verifies the exact 2026 date
boundary, two retrieved nights, a 20000-cent total, and backend-rendered
`$200.00`; no corrected live result or screenshot was claimed at that stage.

The final authorized live run on October 9, 2026 produced the intended matching
result. Its flat SQL used exactly two joins over the three approved tables and
bound `2026-10-10`, `2026-10-12`, two nights, and a limit of 50. The validator
accepted the query, and read-only retrieval returned Hotel State College with
two requested nights, 20 minimum rooms, and `total_cost_cents: 20000`. The
grounded answer named October 10 and 11, identified October 12 as checkout,
displayed `$200.00`, and disclosed that rates and availability are simulated.

The persisted grading identifiers are `C000005`, `M000009`, `M000010`, and
`R000007`, with prompt version
`sha256:40e8a2b6ebd334d5c2ce5f58e7825cd14abbfe6045ac0e8ee85e5ad1a5c7b7ec`.
Browser refresh and full service restart restored the visible conversation with
only local GET requests and no provider replay. The console was clean. Manual
captures were then saved and reviewed. The Network PNG clearly records the two
local history GETs and no advisor POST. The advisor PNG records C000005, the
question, `$200.00` answer, and simulated-data disclosure, but its current crop
does not include the lower SQL, parameters, 20000-cent row, R000007, or prompt
version. The student accepted this crop as supporting submission evidence; the
omitted lower fields remain documented by the visible-browser and automated
verification rather than being attributed to the screenshot itself.

The follow-up read-only restoration slice now rehydrates the complete grading
panel from the latest completed run when a saved conversation is opened. The
public detail response is limited to status, proposed SQL, structured bound
parameters, retrieved records, run ID, and prompt version; Vue obtains the
grounded answer from the persisted assistant message. Visible verification
restored all `C000005`/`R000007` evidence before and after a full service restart
using history GET requests only, with no new advisor POST or provider request.

The backend accepts a natural-language hotel question, asks OpenAI for a
structured SQL proposal, validates and executes one bounded read-only SQLite
query over saved hotels and simulated nightly data, then asks OpenAI for an
answer grounded in the retrieved records. Provider calls are backend-only. The
response includes the question, proposed SQL, bound parameters, retrieved rows,
answer, status, and durable conversation/message/run identifiers.

Additive SQLite tables preserve ordered conversations, user/assistant messages,
prompt version, proposed and executed SQL, parameters, retrieved records,
result status, and safe failures. The Vue panel can start or reopen a
conversation, ask follow-ups, display the complete grading evidence, and reload
history from SQLite. It clearly identifies rates and availability as simulated
course data and keeps advisor failures isolated from the existing ZIP, map,
saved-hotel, booking, and Assignment 1 workflows.

Automated checks use temporary databases and mocked provider responses. The
Vue API client, linters, and production build pass. The October 8 bounded
browser check used the real local Vue/FastAPI/validator/read-only
SQLite/persistence path with deterministic provider mocks. It showed the
question, SQL, parameters, exact rows, grounded answer, simulated-data label,
ordered follow-up history, refresh and restart persistence, safe controlled
failures, local-only request paths, healthy existing travel workflows, and a
console with no warnings or errors. Conversation `C000003` and its four
messages persisted through the final restart; IDs advanced through `M000019`
and `R000012` without reuse. A correct matching live demonstration and its
submission recording remain required before this section is submission-ready.

The October 8 controlled live attempt submitted the required question exactly
once. Vue showed loading and disabled advisor controls, then displayed the safe
service-unavailable message after local HTTP 502. The database retained
`C000001`, user message `M000001`, and failed run `R000001` with no proposed or
executed SQL. The first provider stage therefore failed before retrieval, and
the second provider stage was not called. No retry or screenshot was claimed.
All pre-existing travel-data row counts and content hashes remained unchanged;
only the additive advisor schema, counters, and safe failed-attempt audit record
were added to the ignored development database.

After the malformed local key value was replaced, a sanitized first-stage
diagnostic returned HTTP 200. One authorized Vue request then completed both
live OpenAI stages. Conversation `C000002`, user message `M000004`, assistant
message `M000005`, and run `R000004` persisted through browser refresh and a
full service restart without another provider request. The accepted read-only
query referenced only `saved_hotels`, `saved_hotel_searches`, and
`demo_hotel_nights`; its parameters were `2024-10-10` and `2024-10-12`, so it
retrieved no records. The grounded `no_matches` answer agreed with that empty
result and retained the simulated-data disclosure. This proves the complete
live technical round trip, but the invented 2024 year means it is not yet the
intended matching 2026 submission demonstration. The focused prompt correction
documents the October 10–14, 2026 course-data range, preserves explicit years,
and prohibits inventing another year. No final evidence screenshot is claimed
from the earlier no-match run; a correct live result remains required.

The separately authorized rerun created conversation `C000003`, messages
`M000006` and `M000007`, and run `R000005`. Its proposal used 2026 and passed the
read-only validator, but selected checkout `2026-10-13` rather than the required
`2026-10-12`. It retrieved three nightly rows: 10000, 10000, and 12550 cents.
Although these total 32550 cents (`$325.50`), the displayed answer reported
`$32.55`. Refresh and a full service restart restored the conversation without
another advisor POST, and the browser console remained clean. Because the
answer failed both the expected checkout boundary and exact record grounding,
no corrected success screenshot or recording is claimed.

## Assignment 2 Part 2 chatbot checkpoint

The reviewed implementation and accepted evidence are recorded in
[`acdd832c1a78c0351238ca18f1c54bb6b90340b7`](https://github.com/NateHudson214/hudson-travel/commit/acdd832c1a78c0351238ca18f1c54bb6b90340b7).
The non-fast-forward merge into `main` is
[`6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef`](https://github.com/NateHudson214/hudson-travel/commit/6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef).
The student completed the final manual VS Code review. The full automated,
documentation, evidence, protected-file, ignore, and read-only database gate
passed on both the feature branch and merged `main`. The feature branch and
final merged checkpoint are published at the Hudson Travel repository; upload
of this report and any requested evidence to Canvas remains manual.
