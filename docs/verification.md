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

## Assignment 2 Part 2 local-hotel automated checks

The local-hotel tests use temporary SQLite files. They verify:

- additive, repeatable creation of `saved_hotels`, `saved_hotel_searches`, and
  `demo_hotel_nights` without changing Assignment 1 records;
- exact provider-ID storage, nullable provider name/address, duplicate-save
  protection, and multiple ZIP associations;
- exactly five rows dated October 10–14, 2026 with default 10000-cent rates and
  20 rooms;
- preservation of a manually changed demo rate and room count across a repeated
  save and database reinitialization;
- saved-ID status, stored search context, saved-by-ZIP retrieval, strict ZIP
  validation, and HTTP 200 empty local results;
- safe database errors that do not expose internal details; and
- transactional removal of only the selected provider hotel, its associations,
  and its nights.

The frontend API-client tests verify the exact saved-ID, local ZIP, create, and
delete paths, methods, URL encoding, and JSON body. There is no installed
component-test capability. The production build and manual browser check are
therefore the verification boundaries for the local-first orchestration,
source labels, action states, simulated night table, and list/map selection.

### Observed local-hotel workflow — October 1, 2026

- Preflight confirmed zero rows in all three local-hotel tables. The complete
  gate passed with 123 backend tests, 29 frontend API-client tests, both linters,
  and a 26-module Vite build. Protected hashes and ignore checks passed.
- One authorized ZIP `16802` search requested the empty local collection first,
  then made one live nearby-hotel request. It displayed 20 API results, the
  resolved State College center, list/map markers, and Geoapify/OpenStreetMap
  attribution.
- Scholar Hotel State College and Hotel State College were added through Vue.
  Each POST returned HTTP 201 before saved feedback appeared. SQLite then held
  2 hotels, 2 ZIP associations, and 10 nights: five rows per hotel dated October
  10–14 with 10000-cent and 20-room defaults.
- After refresh, ZIP `16802` displayed only the two saved results with the
  **Saved locally**, incomplete-subset, and simulated-data disclosures. Backend
  logs contained the local GET and no `/api/hotels/nearby` request.
- The student changed Hotel State College on `2026-10-12` to 12550 cents and 7
  rooms in DB Browser and clicked **Write Changes**. Vue then showed `$125.50`
  and 7 without a provider request.
- Scholar Hotel State College was removed through Vue after explicit
  confirmation. HTTP 204 preceded its removal from the interface. SQLite then
  retained only Hotel State College, one ZIP association, and its five nights.
- A complete stop/restart preserved the edited hotel and values, preserved the
  removal, and created no duplicate rows. The post-restart local search again
  made no provider request.
- The fixed and entered-ZIP controls remained present; Harbor Lantern Hotel
  returned T001 and T009; all eight existing booking rows remained; attribution
  remained visible; and the healthy console had no warning or error entries.
- Correction cycle 1 added Leaflet marker `keypress` selection after keyboard
  activation opened the marker popup without updating the list. The complete
  gate passed again, and keyboard list-to-map and map-to-list selection then
  updated `aria-current` correctly. No further correction cycle was required.

### Reviewed Part 2 evidence and cleanup — October 5, 2026

The student captured and reviewed the three repository evidence files and
confirmed that they are readable and contain no API key, secret, private
information, or unrelated content. Visual inspection confirmed:

- `evidence/assignment2-part2-edited-rate.png` — 2880 x 1696 PNG showing ZIP
  `16802`, the **Saved locally** state, Hotel State College, its five simulated
  nights, and the edited October 12 `$125.50` rate with 7 rooms. SHA-256:
  `90eea9cdd5f6f1360842219281e8f0e12335f7c1bd264610a71d373fb04469de`.
- `evidence/assignment2-part2-local-first.png` — 2858 x 1476 PNG showing the
  **Saved locally** result and Safari Network panel with the local
  `saved-hotels` request. No `/api/hotels/nearby` request is present in the
  captured request list. SHA-256:
  `f49cf3440b34cb33273b4160950fa2673bf7eceb375e61b52e4ef3986ae1f543`.
- `evidence/assignment2-part2-database.png` — 2880 x 1792 PNG showing the joined
  SQLite query and exactly five Hotel State College rows for October 10–14,
  including `12550` cents and 7 rooms on October 12. SHA-256:
  `0e6f05ee5de5ddbe5831b7edf68ee722491bda48b58f71e6cdf8a592e1581798`.

Only the Hudson Travel backend and frontend started for the evidence session
were stopped afterward. Ports 8000 and 5173 were confirmed free. The final
manual VS Code review and Git checkpoint were subsequently completed as
recorded below.

### Assignment 2 Part 2 Git checkpoint verification

The final manual VS Code review passed on October 5, 2026. The complete gate
then passed on `assignment2_part2_in_class` and again after its non-fast-forward
merge into `main`. Each run produced 123 passing backend tests with the same two
non-failing dependency warnings, 29 passing frontend API-client tests, clean
Oxlint and ESLint runs, and a successful 26-module Vite build. Dependency
consistency, Markdown links, `git diff --check`, protected hashes, evidence
hashes, and ignore coverage also passed. No live Geoapify request was made.

- Implementation and evidence checkpoint:
  [`77ae9b397caf3a3062d1ae8955aaf30cd0d1456d`](https://github.com/NateHudson214/hudson-travel/commit/77ae9b397caf3a3062d1ae8955aaf30cd0d1456d)
- Non-fast-forward merge checkpoint:
  [`79e0b6ddd0acb1909059ef344d1bc369f78fe25e`](https://github.com/NateHudson214/hudson-travel/commit/79e0b6ddd0acb1909059ef344d1bc369f78fe25e)

The feature branch and final `main` documentation state are published at
<https://github.com/NateHudson214/hudson-travel>. The ignored development
database remains local with one saved hotel, one ZIP association, and five
demo-night rows, including 12550 cents and 7 rooms for October 12.

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

## Assignment 2 Part 2 mocked hotel-advisor backend checks

The backend workflow is verified without live OpenRouter or Geoapify traffic
and without opening the development database. Focused tests replace all three
application-state callables and use the normal temporary test database.

Verify:

1. Missing, blank, non-string, and trimmed questions longer than 500 characters
   return HTTP 400 before proposal, retrieval, or answer generation.
2. A successful request runs proposal, retrieval, and grounded answer once and
   in order. Retrieval receives `app.state.database_path` and the exact
   `QueryProposal`; answer generation receives the normalized question,
   accepted SQL, exact parameters, and exact records.
3. Responses preserve `status`, `question`, `proposed_sql`,
   `query_parameters`, `retrieved_records`, and `answer`, and add conversation,
   message, run, and prompt-version identifiers.
4. `answered` requires nonempty records, `no_matches` requires empty records,
   and `insufficient_data` is accepted for missing required data. Inconsistent
   provider status becomes a safe HTTP 502.
5. Empty valid retrieval still reaches answer generation. Rejected or excessive
   SQL returns 422 before the second model stage; local execution/result failure
   returns 500 before it.
6. Missing configuration returns 503, rate limiting returns 429, and
   authentication, model availability, transport, provider HTTP, or malformed
   output returns a sanitized 502.
7. No response reveals a key, authorization header, provider URL, database
   path, accepted SQL, raw SQLite/provider error, or hidden prompt.

The provider-neutral/OpenAI foundation additionally verifies:

1. Shared query and answer value objects contain no provider-specific fields,
   while existing OpenRouter errors preserve the shared sanitized categories.
2. The explicit repository prompt contains only the three approved tables,
   required joins and query rules, honest simulated-data language, and no key.
   Its version is the SHA-256 of the exact file bytes.
3. Mocked OpenAI calls use only `POST /v1/responses`, the configured model,
   backend authorization, `store: false`, finite timeouts, bounded output, and
   one forced strict function tool.
4. Proposal and answer parsing accepts the three supported answer states and
   rejects missing, incomplete, duplicate, malformed, extra, or inconsistent
   tool results.
5. Missing configuration, authentication, rate-limit, model, HTTP, timeout,
   network, and malformed-response errors remain distinct internally and never
   expose a credential, authorization header, provider URL, or database path.

The route now uses OpenAI by default. Mocked end-to-end tests additionally prove
that a question reaches the first Responses request, accepted SQL executes only
against a temporary read-only database, exact records reach the second request,
and the grading fields return to the caller. Matching, no-match,
insufficient-data, blocked-write, configuration, authentication, rate-limit,
model, HTTP, timeout, network, and malformed-response paths are covered without
live traffic. Mocked Vue integration is recorded below; a live LLM round trip
remains unverified.

### Advisor persistence and follow-up checks

Persistence tests use only temporary SQLite files and mocked OpenAI transports:

1. Repeated initialization creates the three additive advisor tables once and
   preserves every existing Assignment 1 and saved-hotel record.
2. A new request durably creates a conversation, ordered user message, and
   pending run before provider work. Completion records the assistant message,
   prompt version, proposal, executed SQL, exact parameters, bounded records,
   status, and timestamps.
3. Each persistence operation owns a short transaction. Tests do not hold a
   database write transaction while either mocked provider response is pending.
4. A follow-up request reuses its conversation ID and supplies the prior ordered
   user/assistant messages to both mocked Responses calls.
5. Reinitializing the same temporary database retains completed and failed
   history. Independent durable counters prevent ID reuse.
6. Unsafe SQL stops before execution and the second provider call while leaving
   a safe failed run. Configuration, authentication, rate, model, transport,
   HTTP, malformed-output, and retrieval failures likewise retain safe audit
   state when storage is available.
7. Unknown conversation IDs return 404 before provider access. History endpoints
   expose only bounded user-visible messages and never expose prompts, audit
   SQL, error internals, keys, provider URLs, authorization headers, or paths.
8. No automated test makes a live provider request or modifies the ignored
   development database. Browser, live-provider, and refresh/restart results
   are recorded below.

### Vue advisor implementation gate

Frontend API-client tests verify the exact local GET and POST paths,
URL-encoded conversation IDs, normalized new questions with a null conversation
ID, exact follow-up IDs, preservation of every evidence/identifier field, safe
backend details, and fallback behavior for empty or malformed errors.

The implemented panel must later be smoke-tested to prove:

1. Page load lists and reopens persisted history without contacting a provider.
2. A new mocked question shows loading, disables conflicting advisor controls,
   and displays ordered messages, SQL, parameters, records, answer, and status.
3. A mocked follow-up sends the active conversation ID and displays persisted
   ordered history after the backend reread.
4. New conversation clears only current advisor display state and never deletes
   stored history.
5. Validation and mocked 404/422/429/500/502/503 responses show safe feedback,
   retain valid messages, clear stale evidence, and leave every existing travel
   workflow unchanged.
6. Browser refresh and backend/frontend restart restore persisted history from
   SQLite, while the healthy console and Network panel remain credential-free.

No component-test dependency exists, so no component tests were added.

### Mocked advisor browser and persistence smoke test — October 8, 2026

The complete gate passed first: 321 backend tests and 37 frontend API-client
tests passed; the same two non-failing framework dependency warnings remained;
Oxlint, ESLint, the 28-module Vite build, dependency consistency,
documentation, whitespace, protected-file, ignore, and database-preservation
checks passed. Zero source-correction cycles were required.

The browser used the normal Vue client, FastAPI advisor routes, SQL validator,
read-only executor, and persistence layer against one temporary SQLite copy.
Both model stages were deterministic local-only mocks, so no OpenAI,
OpenRouter, or Geoapify request occurred. The first question created
conversation `C000001` and runs `R000001`/`R000002`; its initial answer showed
three retrieved nights and a simulated `$325.50` total, and the follow-up
showed October 12 at `$125.50` with 7 rooms. Later, after a service restart,
the exact required question and follow-up created `C000003`, `R000011`, and
`R000012`; all four messages survived a second full restart.

Loading feedback appeared while the textarea, Ask button, and New conversation
button were disabled. The visible evidence included the question, checked SQL,
bound parameters, exact records, grounded answer, status, conversation ID, run
ID, and safe prompt hash. New conversation cleared only the current display;
reopening restored SQLite-backed messages. Blank input made no POST. Local-only
outcomes visibly verified no-match, insufficient-data, rejected unsafe SQL
(422), unknown conversation (404), rate limit (429), missing configuration
(503), provider failure (502), retrieval failure (500), and history failure
(500). Each message was safe, stale evidence cleared, and prior valid messages
remained visible.

Before final cleanup the temporary database contained three conversations, 19
messages, and 12 runs. IDs were contiguous through `C000003`, `M000019`, and
`R000012`; next counters were 4, 20, and 13, and `foreign_key_check` was empty.
Failed attempts remained recorded, reinitialization created no duplicate rows,
and the browser console had no warnings or errors. The entered-ZIP controls,
saved/local-first result for 16802, selected hotel/map state and attribution,
Harbor Lantern Hotel results T001/T009, and booking history remained intact;
no hotel, booking, or development-database mutation occurred. Live OpenAI
results are recorded below.

### Controlled live OpenAI attempt — October 8, 2026

The complete gate passed before provider traffic: 321 backend tests and 37
frontend API-client tests passed, the same two non-failing framework warnings
remained, both non-fixing linters passed, and the 28-module Vite build,
dependency consistency, documentation links, whitespace, protected-file,
ignore, and read-only database checks passed. One documentation-consistency
correction cycle removed stale statements that the mocked browser check was
still pending.

The sanitized health response reported `status: ok`, both existing provider
keys configured, OpenAI configured, and `openai_model: gpt-6-luna`. The visible
Vue panel submitted the required question exactly once. Loading feedback
appeared while the question, Ask, and New conversation controls were disabled.
The local `POST /api/hotel-advisor` returned HTTP 502 and Vue displayed only
`The hotel advisor service is temporarily unavailable.` Controls recovered and
the browser console had no warnings or errors. No retry, follow-up, model
switch, or evidence screenshot was made.

SQLite recorded conversation `C000001`, user message `M000001`, and failed run
`R000001` with safe category `provider_failure`. Both proposed and executed SQL
were null, so retrieval and the second provider stage did not occur. This was
one attempted OpenAI request, not a successful two-call demonstration. The
startup-created advisor schema and failed audit record changed the database
file checksum as expected; all pre-existing hotel, trip, user, booking,
saved-hotel, search-association, and demo-night row counts and content hashes
remained identical. Integrity and foreign-key checks passed.

### Controlled live OpenAI two-stage result — October 8, 2026

After a sanitized diagnostic identified HTTP 401 `invalid_api_key`, the student
corrected the ignored `OPEN_AI` value without exposing it. A single first-stage
diagnostic then returned HTTP 200. The authorized Vue demonstration created a
new conversation and submitted the required question exactly once. Loading was
visible and conflicting advisor controls were disabled. Backend logs recorded
exactly one local `POST /api/hotel-advisor` returning HTTP 200; no retry or
follow-up occurred.

Both live OpenAI stages completed. The proposed CTE query passed the existing
validator and read-only executor and referenced only `saved_hotels`,
`saved_hotel_searches`, and `demo_hotel_nights`. It bound `checkin` to
`2024-10-10` and `checkout` to `2024-10-12`. Because the retained demo nights
are in 2026, retrieval returned `[]`. The second stage returned status
`no_matches` and a grounded answer stating that no matching saved records were
retrieved and that nightly rates and availability are simulated data. The
answer was consistent with the exact empty retrieval, but the model's invented
2024 year means the intended matching 2026 acceptance result did not pass.

The completed state persisted as conversation `C000002`, user message
`M000004`, assistant message `M000005`, and run `R000004`, with prompt version
`sha256:a162ad0c8c357c291040144c83072a0bb7d835676beef9815a989d993bc03fb1`.
Browser refresh and a full backend/frontend restart restored it without another
advisor POST or provider request. The console contained no warnings or errors.
Pre-existing travel-table row counts and content hashes remained unchanged;
foreign-key integrity passed. No final screenshot was created because this
no-match output does not demonstrate the intended matching answer. A focused
prompt/test correction now explicitly requires 2026 for the yearless October
question and is covered by focused mocked tests. The separately authorized live
rerun is recorded below.

### Corrected-year live rerun — October 8, 2026

One new Vue submission authorized exactly two OpenAI requests and received HTTP
200. The proposal used the corrected year and passed the read-only validator,
but bound `check_in` to `2026-10-10` and `check_out` to `2026-10-13`. It queried
only `saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`, retrieving
the October 10 and 11 rows at 10000 cents and the October 12 row at 12550 cents.
The answer described three nights but reported `$32.55`; the retrieved values
total 32550 cents, or `$325.50`. This failed the required October 12 checkout
boundary and exact grounding checks. No retry occurred and no success evidence
was captured.

The run persisted as conversation `C000003`, messages `M000006` and `M000007`,
and run `R000005`, with prompt version
`sha256:929d2aa1fa49742461662563e2067ea7bb4c23266f51097aa574575f48356173`.
Refresh and full backend/frontend restart restored it using only local GET
requests. The browser console contained no warning or error. Server evidence
showed exactly one local advisor POST; browser-tool Network-panel inspection was
not available, so that specific panel observation remains unverified.

### Date-boundary and cents-grounding correction

Mocked prompt, OpenAI-client, route-integration, validator, and persistence
tests now require the exact demonstration parameters `2026-10-10` and
`2026-10-12`. Temporary retrieval returns two nights, 10000 cents each, as one
`total_cost_cents: 20000` record. The provider must return the exact retrieved
integer plus one `{{total_cost}}` marker; the backend deterministically renders
`$200.00`. Mocked totals of 2000 or 200 cents and free-form `$20.00` are rejected
with the existing sanitized provider-failure response before an assistant
message is persisted. No live request was made for this correction.

### Final authorized live attempt — October 8, 2026

Vue submitted the required question once. The first OpenAI stage returned a
proposal, but the local SQL validator rejected it before execution. The local
endpoint returned HTTP 422 with `The proposed hotel query was rejected for
safety.` The run persisted safely as conversation `C000004`, user message
`M000008`, and run `R000006`, with no assistant message and error category
`unsafe_query`. The grounded-answer request did not run. No retry, refresh,
restart, Network screenshot, console claim, or success evidence was produced.

### Rejected-proposal diagnosis and mocked correction

A read-only diagnostic inspected only the persisted proposal and parameters for
`R000006`; it did not execute the SQL. The proposal used `UNION` and three
joins. The validator correctly rejects compound queries first and would also
reject the join count above two. Its date parameters were the intended
`2026-10-10` and `2026-10-12` values.

The validator was not relaxed. The versioned prompt now requires one flat
`SELECT`, no CTE or compound form, and exactly two joins across the three
approved saved-hotel tables. Mocked route coverage executes that accepted shape
against a temporary database, retrieves only October 10 and 11, returns
`requested_nights: 2`, `minimum_rooms: 20`, and `total_cost_cents: 20000`, and
renders `$200.00` through the existing deterministic backend safeguard. Separate
mocked proposals prove that `UNION` and more than two joins still stop before
retrieval and before the second provider call. No live request was made.

### Corrected live matching result — October 9, 2026

One new Vue conversation submitted the required question exactly once. The
local `POST /api/hotel-advisor` returned HTTP 200 after the two authorized
OpenAI stages. The accepted proposal was one flat parameterized `SELECT`, used
exactly two joins, contained no compound query form, and referenced only
`saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`. Its bound
parameters were `check_in=2026-10-10`, `check_out=2026-10-12`,
`night_count=2`, and `limit=50`.

Read-only retrieval returned one Hotel State College record with
`requested_nights: 2`, `minimum_rooms: 20`, and `total_cost_cents: 20000`.
The displayed answered result identified October 10 and 11, treated October 12
as checkout, disclosed that rates and rooms are simulated demonstration data,
and rendered `$200.00` through the backend safeguard. The persisted identifiers
are conversation `C000005`, user message `M000009`, assistant message `M000010`,
run `R000007`, and prompt version
`sha256:40e8a2b6ebd334d5c2ce5f58e7825cd14abbfe6045ac0e8ee85e5ad1a5c7b7ec`.

The browser console contained no warnings or errors. Backend request evidence
showed one local advisor POST for the live workflow. Browser Network-panel
capture was unavailable through the safe automation interface, so that panel
still requires manual evidence. Browser refresh and a full backend/frontend
restart restored the saved question and answer using only local GET requests;
neither action made another advisor POST or provider request. SQLite integrity
and foreign-key checks passed after the run.

The student saved and reviewed these files:

- `evidence/assignment2-part2-live-chatbot-corrected.png`
- `evidence/assignment2-part2-live-chatbot-network-corrected.png`

Independent inspection confirmed that the Network screenshot is readable and
shows the local conversation-list and `C000005` GET requests without an advisor
POST or credential. The advisor screenshot is also readable and shows C000005,
the required question, the persisted `$200.00` answer, and the simulated-data
disclosure. Its crop ends before the checked SQL, 2026 parameters, 20000-cent
record, R000007, and prompt version. The student accepted the current image as
supporting evidence; those lower fields remain supported by the recorded visible
browser verification and automated response checks.

### Persisted advisor-evidence restoration — October 9, 2026

The conversation-detail endpoint was extended read-only to return the latest
completed run's safe evidence fields. Automated coverage verified structured
parameters and records, exact field exclusion, safe conversations without a
completed run, and exclusion of failed and pending runs. The complete gate
passed with 328 backend tests (the same two non-failing dependency warnings),
38 frontend API-client tests, both linters, and a 28-module production build.

In the visible browser, reopening `C000005` restored its question, persisted
assistant answer, flat checked SQL, `2026-10-10`/`2026-10-12` parameters,
`total_cost_cents: 20000` record, `$200.00`, run `R000007`, prompt version, and
simulated-data disclosure. The same panel returned after stopping and restarting
both services against the unchanged database. Backend logs contained only GET
requests for conversation history and normal application data; there was no
advisor POST or provider replay. The healthy console contained no warnings or
errors. The reviewed Network PNG captures this GET-only restoration, and the
student accepted the companion advisor PNG. Only the retained Hudson Travel
services were stopped afterward, and ports 8000 and 5173 were free.
