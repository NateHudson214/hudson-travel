# Current Handoff

**Updated:** September 29, 2026

**Checkpoint:** Assignment 1 preserved; Assignment 2 Part 1 implementation,
bounded live browser verification, evidence review, and final VS Code review
complete; Git checkpoint pending

## Assignment 2 Part 1 current stage

- The authoritative Part 1 scope is live hotel search and a synchronized map,
  not only the completed entered-ZIP demonstration.
- Research notes are in `docs/assignment2-part1-research.md`.
- The early, explicitly unimplemented design is
  `docs/mockups/assignment2-part1-early.svg`.
- The implemented backend flow resolves the exact U.S. ZIP, then requests up to 20
  `accommodation.hotel` features inside a strict 5,000-metre circle with
  proximity ordering.
- The implemented frontend uses one `selectedPlaceId` so list and map selection
  remain synchronized and keyboard-accessible.
- Hotel fields will remain provider-derived; missing values receive honest
  labels or omission, and no price, rating, availability, or booking claim will
  be invented.
- Geoapify and OpenStreetMap attribution must remain visible.
- `httpx` remains the declared backend HTTP client. Leaflet 1.9.4 is now an
  exact direct frontend dependency following the completed approval step.
- `GET /api/hotels/nearby?zip_code={zip_code}` returns the resolved location,
  5,000-metre radius, 20-result limit, and sanitized provider hotel records.
- Mocked controller and route tests cover request parameters, honest optional
  fields, invalid-feature exclusion, empty success, leading-zero ZIPs, safe
  errors, and coordinate handoff from geocoding to Places.
- Backend verification on September 28, 2026: 38 focused Places/route tests and
  95 complete backend tests passed. The complete suite retained the same two
  non-failing framework dependency warnings.
- Existing frontend verification remained green: 17 API-client tests, Oxlint,
  ESLint, and the 20-module Vite production build passed.
- `NearbyHotelSearch.vue` provides a separate validated ZIP flow with distinct
  initial, loading, validation, unresolved, empty, results, and service-error
  states while preserving both earlier ZIP lookup workflows.
- `NearbyHotelsMap.vue` owns one Leaflet map and replaceable marker layers. The
  parent owns `selectedPlaceId`, so list-button and marker selection stay on one
  provider identity.
- Provider names, addresses, and distances are rendered honestly; Geoapify and
  OpenStreetMap attribution are included, with no commercial travel fields.
- Frontend verification on September 29, 2026: all 23 API-client tests, Oxlint,
  ESLint, and the 25-module Vite production build passed.
- The bounded smoke test on September 29 used exactly one live nearby-hotel
  search for ZIP `16802`. It resolved State College and returned 20 provider
  hotels through the local FastAPI route.
- The live page showed 20 list results and 20 numbered map markers, a distinct
  search-center marker, and visible Geoapify, Leaflet, and OpenStreetMap
  attribution. List-to-marker and marker-to-list selection both passed.
- Local-only mocks verified loading, leading-zero ZIP `02113`, honest missing
  fields, empty results, 404 and 502 feedback, and stale-result clearing.
- All six invalid-input classes produced client validation without a backend
  request. Harbor Lantern Hotel still returned T001 and T009, eight existing
  booking-history records loaded, and no booking was changed.
- The healthy browser console had no warnings or errors. Zero correction cycles
  were required. Shortlist behavior remains unimplemented and outside Part 1.
- The student captured and reviewed all four required evidence files. The three
  PNGs are readable and visibly show the required live, synchronized-selection,
  and validation states. The readable QuickTime recording was manually reviewed
  by the student. No key, secret, private, or unrelated content was reported.
- The retained backend and frontend were stopped after capture; ports 8000 and
  5173 are free.
- The final VS Code review passed. The student confirmed that every visible
  change was intentional, evidence was correct, protected/generated/private
  files were excluded, CSV records were unchanged, and no shortlist or Part 2
  behavior was included.

## Assignment 2 public API activity

- The backend-only Geoapify configuration helper and safe health status are in
  place; the credential is never returned to Vue.
- The fixed `GET /api/demo/zip-location` demonstration remains available and
  was observed resolving ZIP 16802 to State College on September 23, 2026.
- New `GET /api/zip-location?zip_code={zip_code}` accepts a string, trims it,
  and requires exactly five ASCII digits before calling the existing controller.
- The dynamic route preserves leading zeros and maps invalid input, unresolved
  ZIPs, missing configuration, and provider failures to safe 400, 404, 503, and
  502 responses.
- Vue now provides a labeled text input and dynamic lookup action. It validates
  five digits, disables both ZIP actions during a request, clears stale dynamic
  results on failure, and displays success in a plain location table.
- The fixed demonstration, hotel search, and booking interface remain intact.
- Geoapify hotel retrieval, the results list, and the Leaflet map extend the
  earlier ZIP-foundation activity and are now implemented and smoke-tested for
  Assignment 2 Part 1. Shortlist behavior and its new persistence remain
  outside Part 1.

## Assignment 2 automated verification

- Focused backend ZIP-route tests: 19 passed.
- Complete backend suite: 57 passed with the same two non-failing framework
  dependency warnings.
- Frontend API-client tests: 17 passed.
- Oxlint and ESLint: passed without auto-fix and without findings.
- Vite production build: passed; 20 modules transformed.
- No live Geoapify request was made during the implementation gate.
- Dynamic browser verification passed September 23, 2026; the two PNG files and
  student recording remain pending.

## Assignment 2 browser verification

- Live entered ZIP `16802` returned State College, country `us`, latitude
  `40.803167822`, and longitude `-77.861384958` through the local FastAPI path.
- Loading feedback appeared and both ZIP controls were disabled during a
  delayed local-only response.
- A local-only `02113` response retained its leading zero in the table.
- Blank, short, long, alphabetic, punctuation, and Unicode-digit input showed
  the five-digit validation message and no stale result table.
- Local-only unresolved and provider-failure responses showed safe 404 and 502
  feedback and cleared stale results.
- `Harbor Lantern Hotel` still returned T001 and T009.
- The healthy browser console contained no warnings or errors.
- Zero source correction cycles were needed.
- The first attempted automated field clear did not alter the actual value and
  unintentionally repeated the successful 16802 provider request once.
- After backend restoration, unexpected local requests for ZIPs 18042–18050
  appeared from browser activity outside the scripted smoke-test inputs. The
  backend was stopped immediately; the source of those requests was not proven.
- The successful screenshot-ready state was recreated with the exact observed
  live values through a one-request local mock. The mock is stopped. This
  recreated state must not be described as a second live verification.

## Branch state

- Current branch: `main`
- Base: synchronized `main` commit
  `dcfb474d8c156020389ed7d3ba86d483251a3b8a`
- Part 2 implementation commit:
  `2a127bf79e8cb66069b0c1a9695391a8e2924507`
- Non-fast-forward Part 2 merge commit:
  `95635eff2dc77fdf4f6e9dd5b842a62a239e1f3f`
- The feature branch and final merged `main` documentation state are published
  at `https://github.com/NateHudson214/hudson-travel`.
- Part 1 implementation/evidence checkpoint remains
  `d224428019dd6fb7223c4e607aabc108af145577`.

## Corrected behavior

- `GET /api/trips?hotel_name={hotel_name}` reads `hotels.csv` and `trips.csv`
  with `utf-8-sig`, joins through `hotel_id`, and returns associated stays.
- Hotel-name input is trimmed and matched case-insensitively.
- Partial matching is supported; `Lantern` finds Harbor Lantern Hotel.
- Missing and blank hotel names return `400` with
  `Enter a hotel name to search.`
- A valid unmatched hotel name returns `200` with `[]`.
- Vue provides hotel-name search plus loading, validation, request-error,
  no-results, summary, and results-table states.
- Validation and request failures clear stale results.
- The Part 1 search interface remains intact while the Part 2 backend slice is
  developed separately on the feature branch.
- Vue loads the supplied travelers and joined booking history on startup.
- The booking form accepts a traveler and one trip from current search results,
  then sends creation through FastAPI.
- The history table exposes cancellation for confirmed rows and deletion for
  test rows. It refreshes from SQLite after each successful mutation.
- Search and booking failures use independent state, so one workflow does not
  erase valid data from the other.

## Superseded local checkpoint

The two earlier local commits contained the city-search interpretation. They
were never pushed and were replaced by the corrected hotel-search history after
automated checks, browser checks, replacement screenshots, and manual review
passed. The obsolete Boston and Seattle screenshots were removed.

## Verification status

- Corrected automated tests, lint, and build: passed September 10, 2026.
  - Backend pytest: 6 passed with the same two non-failing framework warnings.
  - Frontend API-client tests: 3 passed.
  - Oxlint and ESLint: passed with no findings.
  - Vite production build: passed; 14 modules transformed.
- Corrected API and browser smoke test: passed September 10, 2026.
  - Exact, lowercase, surrounding-space, and partial searches returned T001 and
    T009 with values matching the joined CSV records.
  - The unmatched search showed a clear message without a table.
  - Blank validation and a safely simulated backend outage both cleared stale
    results; the outage displayed a request-error message.
  - The healthy browser console contained no warnings or errors.
  - One correction cycle added visible trip IDs beside trip names, after which
    the complete automated gate and browser checks passed again.
- Replacement screenshot review: passed; both 2878 x 1696 PNGs are readable,
  application-only, and show the required successful and unmatched states.
- Corrected manual VS Code scan: completed by the student; all visible changes
  were intentional, no secrets or `.env` files were present, generated output
  was excluded, and the source CSV files were unmodified.
- Protected-file integrity: CSV and dependency-declaration SHA-256 values match
  the pre-correction values.

## Evidence and remaining placeholders

- `evidence/part1-hotel-search.png` (SHA-256
  `d58cbe7f37151ebf361976357a19b06552c4733059dc285a0d1f9d565a6c7b11`)
- `evidence/part1-hotel-no-results.png` (SHA-256
  `be7c45e845f4b7249665c48f550c68b2b2f05b5335e2b23d68c6bca4fad8457b`)
- Corrected Part 1 implementation/evidence checkpoint:
  `d224428019dd6fb7223c4e607aabc108af145577`
- Public GitHub repository:
  `https://github.com/NateHudson214/hudson-travel`

## Current limitations

- Local dependencies and build output remain ignored and must not be committed.
- Only the student's Part 2 Canvas submission remains pending.

## Part 2 automated verification

- Backend pytest: 15 passed with the same two non-failing framework dependency
  warnings recorded in Part 1.
- Frontend API-client tests: 11 passed, including users, history, exact create,
  cancel, and delete requests, HTTP details, and empty/malformed error bodies.
- Oxlint and ESLint: passed with no findings.
- Vite production build: passed; 18 modules transformed.
- `git diff --check`: passed.
- All four supplied CSV hashes and all three dependency-declaration hashes
  match the Part 1 values.
- Tests used temporary SQLite files; no development database was created.
- `backend/instance/hudson_travel.sqlite3` is covered by `.gitignore`.
- Browser CRUD, refresh persistence, service-restart persistence, controlled
  failure isolation, recovery, and the healthy console all passed.
- Smoke-test database state: B001–B006 plus cancelled B007; B008 absent;
  `csv_seed_version=1`; `next_booking_number=9`.
- Zero source correction cycles were required.
- Only the backend and frontend processes created by the smoke test were
  stopped; ports 8000 and 5173 were released.
- Final manual VS Code review: passed September 14, 2026. The student confirmed
  all visible changes were intentional; no secrets or `.env` files were
  present; generated dependencies, build output, and the ignored SQLite file
  were excluded; and all CSV and dependency declarations were unmodified.

## Next action

Prepare the reviewed Assignment 2 Part 1 feature-branch checkpoint, preserve it
remotely, merge it into `main` with a non-fast-forward merge, rerun the complete
gate, and record the exact hashes and URLs. Do not add shortlist behavior, new
persistence, or begin Part 2.

## Part 2 backend slice

- FastAPI initializes ignored `backend/instance/hudson_travel.sqlite3` at
  startup using Python's built-in `sqlite3`.
- One transaction creates the schema, loads all four UTF-8-sig CSVs with their
  original IDs, stores `csv_seed_version=1`, and initializes the durable booking
  counter at 7.
- Later startups skip all CSV inserts once the marker exists.
- Every application connection enables foreign keys.
- Hotel search now reads SQLite exclusively after initialization.
- `GET /api/users` and `GET /api/bookings` return frontend-ready records.
- `POST /api/bookings` creates confirmed bookings with backend-assigned dates
  and monotonic IDs.
- `PATCH /api/bookings/{booking_id}` cancels while retaining the record.
- `DELETE /api/bookings/{booking_id}` permanently removes the record.
- Temporary-database tests cover seed integrity, repeat initialization,
  SQLite-only search, persistent CRUD, non-reused IDs, joins, and error cases.

## Part 2 frontend slice

- `frontend/src/api/bookings.js` supplies user/history reads and exact
  create/cancel/delete requests through a shared response helper.
- `BookingForm.vue` provides labeled traveler and current-search-trip selectors.
- `BookingHistory.vue` displays joined history and sends cancel/delete events.
- `App.vue` loads users/history at startup, validates creation, shows operation
  feedback, disables conflicting booking controls, and rereads history after
  every mutation.
- The history table remains intact on search failure; search results remain
  intact on booking failure.
