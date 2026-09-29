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
