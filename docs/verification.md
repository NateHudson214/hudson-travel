# Hudson Travel Verification

Run these checks from the repository root unless a different directory is noted.
Do not modify the CSV files during verification.

## Automated checks

```bash
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests
cd frontend
npm test
./node_modules/.bin/oxlint .
./node_modules/.bin/eslint . --no-cache
npm run build
```

The linters are invoked without auto-fix so verification does not change source
files.

The backend suite now uses temporary SQLite databases and verifies both Part 1
search behavior and the first Part 2 backend slice:

- exact seed counts and IDs for all four CSV files;
- repeated initialization without duplication or restoration;
- SQLite-only hotel search after initialization;
- B007 creation and B008 allocation after B007 is deleted;
- persistent creation, cancellation, and deletion after reinitialization;
- joined user and booking-history responses; and
- clear errors for missing users, trips, and bookings.

No automated test writes `backend/instance/hudson_travel.sqlite3`.

The frontend API-client suite verifies traveler and history reads, the exact
JSON create and cancellation bodies, deletion with an empty `204` response,
backend error details, and friendly fallbacks for empty or malformed error
responses.

## Assignment 2 ZIP lookup checks

The backend route tests cover the fixed demonstration and the entered-ZIP
contract:

- `16802`, `02113`, and surrounding whitespace pass the normalized five-digit
  string to the controller;
- missing, blank, short, long, alphabetic, punctuation, Unicode-digit, and mixed
  input return HTTP 400 without calling the provider controller;
- unresolved, unconfigured, and provider-failure outcomes map to sanitized 404,
  503, and 502 responses; and
- no labeled fake credential or raw provider detail appears in an error.

The frontend client tests cover the exact local GET path, URL encoding, leading
zero preservation, successful parsing, backend details, and empty or malformed
error fallbacks. No automated test contacts Geoapify.

## Assignment 2 Part 1 nearby-hotel backend checks

The Places-controller and combined-route tests use only labeled mock provider
responses. They verify:

- category `accommodation.hotel`, a strict 5,000-metre circle, matching
  proximity bias, and limit 20;
- longitude-before-latitude ordering in Geoapify request parameters;
- provider place ID, optional name/address, valid coordinates, and optional
  distance sanitization;
- exclusion of features without a usable place ID or finite coordinates;
- HTTP 200 with an empty `hotels` list for a valid empty result;
- leading-zero ZIP preservation and use of the geocoder's returned center;
- safe 400, 404, 503, and 502 route mappings; and
- sanitized malformed, timeout, network, HTTP, and missing-configuration
  failures without credentials or raw provider URLs.

No automated test makes a live Geoapify geocoding or Places request. The live
Places results and browser behaviors were verified separately in the bounded
September 29 smoke test recorded below.

On September 28, 2026, the focused Places/controller route selection passed 38
tests and the complete backend suite passed 95 tests with the same two
non-failing framework dependency warnings. The unchanged frontend passed all 17
API-client tests, Oxlint, ESLint, and a 20-module Vite production build.

## Assignment 2 Part 1 frontend checks

The nearby-hotel API-client tests verify the exact local GET route and method,
URL encoding, leading-zero preservation, a full success response, an empty hotel
array, safe backend details, and empty or malformed error fallbacks. The Vite
production build verifies that Leaflet 1.9.4 and its CSS bundle successfully.
No component-test dependency is installed, so the following behaviors require
the bounded browser smoke test:

1. Enter `16802`, select **Search nearby hotels**, and observe loading with the
   nearby ZIP input and button disabled.
2. Confirm the resolved center and every list field match the local
   `/api/hotels/nearby?zip_code=16802` response.
3. Confirm the list and Leaflet map show the same provider hotels and no
   invented price, rating, availability, or booking claims.
4. Select a list result and confirm the same marker is emphasized and its popup
   opens; select another marker and confirm the corresponding list button has
   `aria-current="true"` and selected styling.
5. Confirm the ZIP search-center marker is distinct, Geoapify attribution is
   visible beside the list, and OpenStreetMap attribution is visible on the
   map.
6. Verify invalid, unresolved, no-hotels, and service-failure states with
   local-only mocks where appropriate. Each failure must clear stale results,
   markers, and selection.
7. Verify the fixed ZIP demonstration, entered-ZIP location table, Assignment 1
   hotel search, and booking history remain usable.
8. Check the healthy browser console and Network panel for application errors,
   provider calls from Vue, or credential exposure.

On September 29, 2026, all 23 frontend API-client tests, Oxlint, ESLint, and a
25-module Vite production build passed. No service was started and no live
Geoapify or browser verification occurred during this implementation gate.

### Observed nearby-hotel smoke test — September 29, 2026

The complete gate was rerun before browser verification: 95 backend tests and
23 frontend API-client tests passed; Oxlint and ESLint reported no findings;
and the 25-module Vite production build succeeded. The backend emitted the same
two non-failing framework dependency warnings. Documentation, protected CSV
and dependency checksums, and ignore coverage also passed.

Exactly one authorized live Vue search used ZIP `16802`. The backend recorded
one HTTP 200 request to the local
`/api/hotels/nearby?zip_code=16802` route. It resolved State College, country
`us`, latitude `40.803167822`, and longitude `-77.861384958`, with the stated
5,000-metre radius and 20-result limit. Geoapify returned 20 hotels. The page
showed 20 list buttons and 20 numbered hotel markers, a distinct red search
center, `Powered by Geoapify`, Leaflet attribution, and OpenStreetMap
contributors attribution. No API key, provider URL, price, rating,
availability, room, or booking claim appeared in the rendered nearby-hotel
workflow.

Selecting **Hotel State College** in the list set that button's
`aria-current="true"` and opened the matching popup. Selecting the map marker
for **Hyatt Place State College** moved selection to the corresponding list
button and opened its matching popup. The browser console contained no warnings
or errors. The fixed and entered-ZIP controls remained present, booking history
loaded eight existing records, and `Harbor Lantern Hotel` still returned T001
and T009. No booking mutation was performed.

A removed local-only mock, with no Geoapify calls, verified delayed loading and
disabled controls; leading-zero ZIP `02113`; honest `Name unavailable` and
`Address unavailable` fallbacks; resolved-empty, unresolved 404, and provider
502 states; and stale location, list, marker, and selection clearing. Blank,
short, long, alphabetic, punctuation, and Unicode-digit values all displayed
`Enter a five-digit U.S. ZIP code.`, cleared the result presentation, and made
no backend request. The normal backend was restored afterward. Zero correction
cycles were required.

The student completed and reviewed all four repository evidence files. The
three PNGs are readable and were visually inspected; the QuickTime recording is
readable and was manually played and reviewed by the student. No key, secret,
private information, or unrelated content was reported:

- `evidence/assignment2-part1-live-hotels.png` — 2876 x 1696 PNG, SHA-256
  `77fde335139eb798d759f5fd4c41e3450e1a20219e5e1aac93c7a7f41b04232d`
- `evidence/assignment2-part1-selection.png` — 2870 x 1692 PNG, SHA-256
  `f0005dbea808d5423e6ea61678c61af8e256ac6a7fb2c95b78884cdaf85a1197`
- `evidence/assignment2-part1-states.png` — captured, 914 x 720 PNG, SHA-256
  `2b08b1eb9f2442487f4359d9a35798a0fa06b63fff834aa4ef5e9accbefdbbc3`
- `evidence/assignment2-part1-demo.mov` — 47,870,865-byte QuickTime movie,
  SHA-256
  `3ff4516cd2692745703255f0718898835d85ac521dd0c8b1af649401f3b38b17`

After evidence capture, only the retained Hudson Travel backend and frontend
were stopped. Ports 8000 and 5173 were confirmed free.

The student completed the final Assignment 2 Part 1 VS Code review on September
29, 2026. Every visible change was confirmed intentional; the four evidence
files were correct and readable; secrets, generated output, caches, the ignored
SQLite database, editor settings, and unrelated files were excluded; supplied
CSV records were unchanged; and no shortlist or Part 2 behavior was present.

### Assignment 2 Part 1 Git checkpoint verification

The complete gate passed on the `assignment2-part1-live-hotels` feature branch
before commit and again on merged `main`. Both runs produced 95 passing backend
tests with the same two non-failing dependency warnings, 23 passing frontend
API-client tests, clean Oxlint and ESLint runs, and a successful 25-module Vite
production build. Dependency consistency, `git diff --check`, local Markdown
links, key-free configuration, frontend secret scanning, protected hashes,
evidence hashes, and ignore rules also passed.

- Implementation/evidence checkpoint:
  [`0f38ae0ac35808e332ec91472bb0d5393e5adfc8`](https://github.com/NateHudson214/hudson-travel/commit/0f38ae0ac35808e332ec91472bb0d5393e5adfc8)
- Non-fast-forward merge checkpoint:
  [`6739c4e5b4e4a93b74d6558253078024b1aa7cbf`](https://github.com/NateHudson214/hudson-travel/commit/6739c4e5b4e4a93b74d6558253078024b1aa7cbf)

The feature branch and final `main` documentation state are published at
<https://github.com/NateHudson214/hudson-travel>. Assignment 1 commits remain
in history, and no live Geoapify request was made during either Git gate.

### Entered-ZIP browser smoke test

1. Confirm the fixed **Look up ZIP 16802** control still displays its location.
2. Enter `16802`, submit the dynamic form, and confirm the plain table shows the
   same postcode, locality, country code, latitude, and longitude returned by
   the local FastAPI response.
3. Confirm the browser requests only `/api/zip-location?zip_code=16802`, with no
   API key in the URL or response.
4. Check blank, short, long, alphabetic, punctuation, and Unicode-digit values.
   Each must show validation feedback, make no request, and clear any earlier
   dynamic result.
5. Use local-only mocked responses to demonstrate leading-zero preservation,
   unresolved ZIP feedback, and provider-failure feedback without consuming
   Geoapify quota. Restore normal behavior afterward.
6. Confirm the original hotel search and booking interface remain intact and
   the healthy browser console has no application errors.

### Observed September 23, 2026

The implementation gate passed: 19 focused ZIP-route tests, 57 complete backend
tests with two non-failing dependency warnings, 17 frontend API-client tests,
clean Oxlint and ESLint runs, and a successful Vite production build with 20
modules transformed. Documentation, checksums, ignore rules, and scope checks
also passed.

The entered-ZIP browser flow returned `16802`, `State College`, `us`, latitude
`40.803167822`, and longitude `-77.861384958`. The local backend log showed
`GET /api/zip-location?zip_code=16802` with HTTP 200; neither the local request
path nor the rendered response contained the API key. A delayed local-only mock
proved that both ZIP buttons disable during loading and that `02113` remains a
five-character string in the request and table. Local-only 404 and 502 outcomes
displayed `ZIP 00000 could not be resolved.` and `The location service is
temporarily unavailable.` and removed the previous table.

Blank, short, long, alphabetic, punctuation, and Unicode-digit values all
displayed `Enter a five-digit U.S. ZIP code.`, cleared the previous dynamic
table, and did not intentionally call the backend. `Harbor Lantern Hotel` still
returned T001 and T009, and the healthy browser console had no warnings or
errors. No source correction cycle was required.

The automation tool failed to clear the field on its first blank-input attempt,
so it unintentionally repeated the successful 16802 lookup once. After normal
behavior was restored, additional local requests for ZIPs 18042 through 18050
were detected from browser activity outside this test's scripted inputs; the
backend started by this run was stopped immediately to protect quota. No key or
provider URL appeared in the observed logs. The frontend was retained at that
time for the earlier activity's manual evidence capture and was stopped later.
Those earlier entered-ZIP evidence placeholders are separate from the completed
Assignment 2 Part 1 hotel-list-and-map evidence recorded above.

## Development services

The backend uses `127.0.0.1:8000` and the Vite frontend uses
`127.0.0.1:5173`. Check both ports before starting services, and never stop a
process that the current verification run did not start.

Start the backend from the repository root:

```bash
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Start the frontend from `frontend/`:

```bash
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Verify the API through the frontend origin:

```text
GET http://127.0.0.1:5173/api/trips?hotel_name=Harbor%20Lantern%20Hotel
Expected: 200 and the two joined stay records T001 and T009

GET http://127.0.0.1:5173/api/trips?hotel_name=Not%20a%20Real%20Hotel
Expected: 200 []

GET http://127.0.0.1:5173/api/trips?hotel_name=%20%20%20
Expected: 400 {"detail":"Enter a hotel name to search."}
```

## Browser checks

Open <http://127.0.0.1:5173> and confirm:

1. Searching `Harbor Lantern Hotel` displays `T001` and `T009` with trip, hotel,
   city, state, dates, and nightly rate matching the joined CSV records.
2. Searching `harbor lantern hotel` and `  Harbor Lantern Hotel  ` produces the
   same two stays.
3. Searching the partial name `Lantern` displays the same two stays.
4. Searching `Not a Real Hotel` displays a clear no-results message and no table.
5. Submitting a blank or whitespace-only hotel name displays a validation error and
   removes results from the previous search.
6. A failed backend request displays an error rather than a no-results message.
7. No application errors appear in the browser console.

After verification, stop only the backend and frontend processes started for
this run.

## Part 2 API checks

The Part 2 interface uses these backend contracts:

```text
GET /api/users
Expected: 200 with U001 through U006

GET /api/bookings
Expected: 200 with six joined seed bookings on a fresh database

POST /api/bookings with {"user_id":"U006","trip_id":"T001"}
Expected: 201, a new unique B-number, booked_on assigned by the backend, and
status "confirmed"

PATCH /api/bookings/{booking_id} with {"status":"cancelled"}
Expected: 200 and the retained booking with status "cancelled"

DELETE /api/bookings/{booking_id}
Expected: 204 and permanent removal
```

After restarting the backend against the same development database, confirm
that additions and cancellations remain, deletions remain deleted, no starter
row is restored, and no seed row is duplicated.

## Part 2 browser CRUD and restart-persistence smoke test

This is a deliberately destructive development-database test and must be run
only after the source implementation gate passes. Do not delete or replace
`backend/instance/hudson_travel.sqlite3` if it contains work that must be kept.

1. Start both services and open <http://127.0.0.1:5173>.
2. Confirm six seeded bookings are visible and the traveler selector contains
   `U001` through `U006`.
3. Search `Harbor Lantern Hotel`; select `U006` and `T001`; create a booking.
   On a fresh database, expect `B007`, `confirmed`, and immediate visibility in
   the refreshed history table.
4. Refresh the browser and confirm the new booking remains.
5. Cancel the new booking in Vue; confirm it remains visible with `cancelled`
   status after the refreshed history response.
6. Create a second test booking through Vue. On a fresh database, expect
   `B008`. Delete that second booking in Vue and confirm it disappears only
   after the request completes.
7. Stop only the two test services, restart both against the same database, and
   refresh the browser. Confirm the cancelled booking remains, the deleted
   booking remains absent, there are no duplicate seed records, and the next
   created booking would not reuse a deleted ID.
8. Safely test a backend outage: preserve visible search results and booking
   history, stop only the test backend, and attempt a booking action. Confirm a
   clear error appears, valid search results are not erased, and existing
   history remains visible. Restart the backend before continuing.
9. Confirm the healthy browser console has no application errors and record
   expected versus observed results in `report.md` and `handoffs/current.md`.

### Observed September 14, 2026

The complete automated gate passed before browser mutation: 15 backend tests
with two non-failing dependency warnings, 11 frontend API-client tests, clean
Oxlint and ESLint runs, an 18-module Vite production build, `git diff --check`,
protected hashes, and database-ignore checks.

The browser test began from a fresh development database. Vue displayed the six
seed bookings and travelers U001–U006, and `Harbor Lantern Hotel` returned T001
and T009 with the expected Boston rows. Vue created B007 for U006/T001 with
backend date `2026-09-14`; B007 remained after browser refresh and remained in
history after cancellation with `cancelled` status. Vue then created B008 for
U006/T009 and deleted it after backend confirmation. B008 stayed absent after a
browser refresh and after both services restarted.

Post-restart database inspection found 8 hotels, 12 trips, 6 users, and 7
bookings: unchanged B001–B006 plus cancelled B007. B008 was absent,
`csv_seed_version=1`, and `next_booking_number=9`, proving no reseed and no ID
reuse. During the controlled backend outage, a failed Vue create showed
`Booking could not be created. Please try again.` while the two search rows and
all seven history rows remained visible. Backend recovery and **Refresh
history** cleared the error. The healthy console contained no warnings or
errors. Service logs recorded the Vue-driven GET, POST, PATCH, DELETE, and
follow-up GET requests. Zero source correction cycles were required, and only
the smoke-test services were stopped afterward.
