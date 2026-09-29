# Hudson Travel — Project Design

**Status:** Assignment 1 remains preserved and published. Assignment 2 Part 1 research, implementation, bounded live verification, evidence review, final VS Code review, feature-branch checkpoint, non-fast-forward merge, and merged-main gate are complete. The reviewed checkpoint is published in the Hudson Travel repository; only Canvas submission remains pending.

## Design revision

The detailed checkpoint instructions materially replace parts of the earlier plan. Part 1 is now a working CSV-backed search checkpoint rather than planning only. The custom six-hotel catalog and JSON booking store are removed. Hudson Travel will use the instructor's records and fixed trip dates. Part 2 will seed SQLite once from all four CSV files and provide booking CRUD through the Vue interface, including cancellation and deletion. These changes are required by the updated assignment rather than optional scope growth.

## Application scope

Hudson Travel adapts the course calculator project into a small local hotel application with a Vue frontend, a Python backend, and FastAPI communication between them. Part 1 lets a user search by hotel name and displays that hotel's matching offered stays from joined hotel/trip records in a plain table. Part 2 moves the supplied data into SQLite and adds simulated booking history with create, read, cancel, and delete actions. All identities, trips, and bookings are synthetic; the application does not connect to Expedia or perform real purchases.

## Assignment 2 graded ZIP lookup

The guided demonstration keeps one button for ZIP `16802`. Vue calls the local
FastAPI route, the Python controller contacts Geoapify with a backend-only key,
and Vue renders the sanitized location response. The graded extension adds a
text input so leading-zero ZIP codes remain intact. Both frontend and backend
require exactly five ASCII digits; the backend trims surrounding whitespace and
is the authoritative validation boundary.

`GET /api/zip-location?zip_code={zip_code}` passes only validated input to the
existing controller. It returns postcode, country code, latitude, longitude,
and locality when supplied. Invalid input maps to HTTP 400, unresolved ZIPs to
404, missing configuration to 503, and provider failures to 502. Vue displays a
successful entered lookup in a plain table and clears stale dynamic results on
validation or request failure. The original fixed route remains unchanged.

The earlier graded activity ended at location lookup, but the authoritative
Assignment 2 Part 1 scope continues from that foundation. Part 1 must retrieve
`accommodation.hotel` places within a strict 5 km circle centered on the exact
resolved U.S. postcode, then present the provider results in a synchronized
Vue list and Leaflet map. It must preserve honest missing-data behavior,
distinct invalid/unresolved/empty/failure states, keyboard access, and visible
Geoapify, OpenStreetMap, and tile-provider attribution. The persistent
shortlist remains Assignment 2 Part 2 and is not part of the current work.

The research record and early mockup are documented in
[`docs/assignment2-part1-research.md`](assignment2-part1-research.md) and
[`docs/mockups/assignment2-part1-early.svg`](mockups/assignment2-part1-early.svg).

### Assignment 2 Part 1 backend contract

`GET /api/hotels/nearby?zip_code={zip_code}` reuses the exact five-ASCII-digit
validation and geocoding behavior, then calls the focused Places controller
with the geocoder's returned coordinates. The controller requests
`accommodation.hotel` with a strict `circle` filter of 5,000 metres, a matching
proximity bias, and a 20-result limit. It returns only provider place ID,
optional name and formatted address, valid coordinates, and optional distance.
Features without a usable provider ID or coordinates are excluded rather than
repaired with invented data.

The combined response contains the resolved `location`, `radius_meters: 5000`,
`result_limit: 20`, and `hotels`. A valid empty provider result is HTTP 200 with
an empty list. Invalid ZIP, unresolved ZIP, missing configuration, and provider
failure map to safe 400, 404, 503, and 502 responses. Mocked tests cover the
contract, and one authorized live search on September 29, 2026, resolved ZIP
`16802` and returned 20 sanitized hotel results through the local route.

### Assignment 2 Part 1 frontend contract

The new nearby-hotel section preserves both earlier ZIP lookup workflows and
calls only `/api/hotels/nearby?zip_code={zip_code}`. It validates five ASCII
digits, disables its controls while loading, and clears the resolved location,
hotel list, marker data, and selection before each request or on failure. A
resolved ZIP with no hotels keeps its location context and shows a specific
empty result rather than a provider error.

The parent nearby-hotel component owns one `selectedPlaceId`. Keyboard-operable
list buttons and Leaflet marker clicks both update that value; the matching row
and marker receive the selected treatment. The focused map component creates
one Leaflet map, replaces its center and hotel layers together, fits valid
points with a maximum zoom, and removes the map on component cleanup. It uses
standard OpenStreetMap HTTPS tiles with Leaflet's visible attribution control.
Hotel results separately display `Powered by Geoapify`. The bounded browser
smoke test verified the live 20-hotel list and 20 hotel markers, visible
Geoapify and OpenStreetMap attribution, list-to-marker and marker-to-list
selection, honest missing-data behavior, safe local-only failure states, and a
clean browser console. No source correction cycle was required.

## Public visual reference

Expedia was observed as a signed-out public visitor on September 9, 2026. The reference screenshots influence information hierarchy only: grouped search controls, readable result summaries, a clear property-selection action, and a purposeful empty history state. Hudson Travel will not reproduce Expedia branding, photographs, advertisements, maps, reviews, account features, or exact layouts.

- Hotel search: <https://www.expedia.com/Hotels>
- Hotel search results: <https://www.expedia.com/Hotel-Search>
- Signed-out Trips page: <https://www.expedia.com/trips>
- Public booking lookup: <https://www.expedia.com/trips/booking-search?view=SEARCH_BY_ITINERARY_NUMBER_AND_EMAIL>

The four source screenshots remain on the student's Desktop and are not yet repository evidence. Before use, crop them to relevant webpage content. The Trips screenshot must remove the visible Codex sidebar and account name.

## Supplied data

The CSV files were inspected without modification. Their headers contain a UTF-8 byte-order mark, so Python should read them with `encoding="utf-8-sig"`.

| File | Records | Columns | Purpose |
| --- | ---: | --- | --- |
| `hotels.csv` | 8 | `hotel_id`, `hotel_name`, `city`, `state`, `nightly_rate_usd` | Hotel identity, location, and nightly price. |
| `trips.csv` | 12 | `trip_id`, `hotel_id`, `trip_name`, `check_in`, `check_out` | Offered fixed-date stays connected to hotels. |
| `users.csv` | 6 | `user_id`, `display_name` | Demo travelers used by bookings. |
| `bookings.csv` | 6 | `booking_id`, `user_id`, `trip_id`, `booked_on`, `status` | Seeded booking records connecting travelers to trips. |

All supplied foreign-key references were checked and resolved successfully: no trip references a missing hotel, and no booking references a missing user or trip.

### Record relationships

```text
hotels.hotel_id  1 ──── * trips.hotel_id
trips.trip_id    1 ──── * bookings.trip_id
users.user_id    1 ──── * bookings.user_id
```

A booking reaches its hotel through two joins:

```text
booking.trip_id → trip.trip_id
trip.hotel_id   → hotel.hotel_id
```

The supplied data demonstrates both one-to-many cases. For example, hotel `H001` has trips `T001` and `T009`, while user `U001` has bookings `B001` and `B002`. Existing IDs must remain unchanged. Part 2 must generate unique IDs for new records.

### Available Part 1 hotel searches

The Part 1 join produces these expected stay counts by exact hotel name:

| Search hotel | Matching offered stays |
| --- | ---: |
| Harbor Lantern Hotel | 2 |
| Maple Square Inn | 2 |
| Metro Garden Hotel | 2 |
| Riverside Studio Hotel | 1 |
| Liberty Lane Inn | 1 |
| Museum Walk Hotel | 1 |
| Capitol Grove Hotel | 2 |
| Valley Trail Inn | 1 |

These counts provide simple expected results for browser verification and backend tests.

## Responsibilities by application layer

| Layer | Part 1 responsibility | Part 2 responsibility |
| --- | --- | --- |
| Interface | Vue provides a hotel-name input, Search button, result table, loading/error feedback, and no-results message. | Vue loads travelers and booking history, creates bookings from a selected traveler and displayed trip, retains cancelled rows, deletes confirmed test rows, refreshes from the backend after mutations, and shows independent loading/success/error/empty states. |
| Logic | Python trims and validates the hotel-name query, performs case-insensitive partial matching, joins trips to hotels through `hotel_id`, and returns predictable results. | Implemented backend logic validates references, assigns durable unique IDs, reads joined history, cancels while retaining records, and deletes selected bookings. |
| Data | `hotels.csv` and `trips.csv` were read-only Part 1 sources. | Implemented initialization seeds all four read-only CSVs once. Every application read and write then uses SQLite. |
| Persistence | No user-created state was required. | Implemented SQLite transactions and a durable seed marker preserve additions, cancellations, and deletions without duplicating or restoring starter records. Browser refresh and full process-restart persistence passed against the development database. |

## Part 1 — CSV Hotel Search

**Due:** Friday, September 11, 2026, at 11:59 PM ET.

### Smallest compliant behavior

1. The page displays a labeled hotel-name input and a **Search** button.
2. The user enters a supplied hotel name such as `Harbor Lantern Hotel`.
3. Vue sends the hotel name to a FastAPI endpoint.
4. The Python backend reads `hotels.csv` and `trips.csv` with `utf-8-sig` handling.
5. The backend joins every trip to its hotel using `hotel_id` and matches the hotel name case-insensitively, including partial names.
6. FastAPI returns matching offered stays as JSON.
7. Vue displays the results in a plain table with clear labels.
8. A valid hotel name with no matches displays a clear message instead of an empty unexplained table.

No date picker, traveler selector, city filter, price filter, booking form, image gallery, or SQLite database is needed for Part 1.

### Recommended endpoint contract

```text
GET /api/trips?hotel_name=Harbor%20Lantern%20Hotel
```

Each returned row should contain only the fields needed by the table:

```text
trip_id
trip_name
hotel_id
hotel_name
city
state
nightly_rate_usd
check_in
check_out
```

The backend should return `200` with an empty JSON list for a well-formed hotel name that has no matches. A missing or blank hotel name should return a clear client error. The frontend should distinguish the no-results response from a backend/network failure.

### Recommended result table

Use these visible columns:

| Trip | Hotel | City | State | Check-in | Check-out | Nightly rate |
| --- | --- | --- | --- | --- | --- | ---: |

IDs may remain in the API response for later use without occupying prominent table columns.

### Part 1 acceptance checks

- Searching `Harbor Lantern Hotel` displays offered stays `T001` and `T009`.
- Lowercase and surrounding-space versions produce the same two results.
- Searching the partial name `Lantern` produces the same two results.
- Searching `Not a Real Hotel` displays a clear no-results message.
- Submitting a blank hotel name displays a clear validation message and does not show stale results.
- The browser table values agree with the joined CSV records.
- A manual VS Code scan finds no unrelated changes, generated dependencies, secrets, or modified source CSV records.

## Part 2 — SQLite Booking CRUD

**Due:** Tuesday, September 15, 2026, at 11:59 PM ET.

### Database initialization

The backend now creates `backend/instance/hudson_travel.sqlite3` during FastAPI startup. In one `BEGIN IMMEDIATE` transaction it creates `hotels`, `trips`, `users`, `bookings`, and `app_metadata`; seeds all four supplied CSVs while preserving every provided ID; stores `csv_seed_version=1`; and initializes `next_booking_number` to 7. The ignored `backend/instance/` directory keeps local state out of Git.

The durable seed marker, rather than row counts or individual record checks,
prevents all later reseeding. The marker is written only after the full seed
succeeds, so a failed transaction cannot record a partial initialization. After
initialization, every application read and write uses SQLite rather than
rereading CSV files.

Foreign keys are enabled on every application connection. New IDs come from a
durable counter reserved inside `BEGIN IMMEDIATE`; cancellation and deletion do
not decrement it, so IDs cannot be reused.

### Required frontend-driven CRUD

- **Create:** Select a supplied demo traveler and offered trip, then create a booking with a new unique booking ID.
- **Read:** Display seeded and newly created bookings in history, including connected traveler, trip, and hotel information.
- **Update:** Cancel a booking by changing its status to `cancelled` while retaining the record.
- **Delete:** Delete a chosen test booking through an explicit frontend action.

The frontend must send each operation through FastAPI to Python; it must not mutate a local-only booking list.

### Implemented Vue interaction

On startup Vue requests both `/api/users` and `/api/bookings`. Hotel search
continues to populate the offered-stay table; the booking form permits only a
trip from those current results to be selected. Creation sends the chosen IDs
to FastAPI. The history table identifies the booking, traveler, trip, hotel,
stay dates, backend-assigned booking date, and status. Confirmed rows expose a
cancel action, all rows expose delete, and a manual history refresh remains
available. Each mutation is followed by a new history request, so SQLite—not a
frontend-only edit—is the displayed source of truth. Booking failures leave
valid search results intact, and search failures leave valid history intact.

### Implemented backend API surface

```text
GET    /api/trips?hotel_name={hotel_name}
GET    /api/users
GET    /api/bookings
POST   /api/bookings
PATCH  /api/bookings/{booking_id}
DELETE /api/bookings/{booking_id}
```

`POST /api/bookings` accepts `user_id` and `trip_id`, assigns `booked_on` and a
new `B` identifier on the backend, creates a `confirmed` booking, and returns
HTTP 201 with joined user/trip/hotel details. `PATCH` accepts only
`{"status":"cancelled"}` and returns the retained joined record. `DELETE`
returns HTTP 204. Missing bookings and nonexistent user/trip references return
clear 404 responses. The history collection is the required read operation, so
no single-booking endpoint is included.

### Part 2 persistence checks

1. Create a booking through Vue and confirm it appears in history.
2. Refresh the browser and confirm it remains.
3. Cancel it through Vue and confirm the record remains with `cancelled` status.
4. Delete a test booking through Vue and confirm it disappears.
5. Restart both frontend and backend.
6. Confirm the new booking and cancellation remain, the deletion remains deleted, and no seed row is duplicated or restored.

## Part 1 checkpoint files

The smallest inspectable Part 1 repository should contain or update the following. Existing course-calculator configuration should be reused where suitable rather than regenerated.

```text
hudson-travel/
├── .gitignore
├── AGENTS.md
├── README.md
├── report.md
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── data/
│   │   ├── hotels.csv
│   │   ├── trips.csv
│   │   ├── users.csv
│   │   └── bookings.csv
│   └── tests/
│       └── test_search.py
├── docs/
│   └── design.md
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.vue
│       └── components/
│           ├── StaySearch.vue
│           └── StayResultsTable.vue
├── handoffs/
│   └── current.md
└── prompts/
    └── 001-part1-hotel-search.md
```

The exact starter files may differ. The folder map should describe the files that actually exist after adaptation rather than forcing unnecessary files.

## Part 1 documentation and submission evidence

- `README.md`: setup and run instructions for Vue and FastAPI.
- `AGENTS.md`: concise project-specific instructions, including CSV preservation and verification expectations.
- `docs/design.md`: this design, updated to match the implemented repository.
- `prompts/`: selected major instructions that influenced the work.
- `handoffs/current.md`: truthful current state, completed checks, limitations, and next Part 2 task.
- `report.md`: the required Part 1 report with repository/commit, implementation responsibilities, expected-versus-observed verification, and links to project context.
- Repository screenshots: at minimum, evidence of one successful hotel-name search and one no-results search. Reference screenshots may also be included after privacy cropping and attribution.

The reviewed Part 1 work must be committed and pushed, and the exact commit must be recorded in `report.md`. Substantial Part 2 work should occur on a feature branch while preserving this checkpoint.

## Technology decisions

- **Vue frontend:** Reuses the course project approach and keeps form state and table rendering easy to inspect.
- **Python backend:** Reads the supplied CSV files directly in Part 1 and manages SQLite in Part 2.
- **FastAPI:** Provides a visible JSON boundary between frontend and backend under the `/api` prefix.
- **CSV in Part 1:** Matches the checkpoint requirement and makes the `hotel_id` join explicit.
- **SQLite in Part 2:** Supports persistent relational CRUD while remaining local and understandable.

Follow **CHECK → TAKE ACTION → VERIFY** before adding dependencies. Inspect the existing manifests and imports first, install only what is missing and required, and record the resulting verification.

## Current state and next implementation task

The project folder is named `hudson-travel`. The corrected Part 1 FastAPI endpoint reads unchanged copies of `hotels.csv` and `trips.csv`, joins records by `hotel_id`, and validates a trimmed, case-insensitive hotel-name query with partial matching. The Vue interface provides hotel-name search, loading, validation, error, no-results, summary, and results-table states.

Project-local dependencies remain installed in ignored directories. Corrected verification produced six passing backend tests, three passing frontend tests, clean Oxlint and ESLint runs, and a successful Vite production build. Exact, lowercase, surrounding-space, partial, unmatched, blank, and safe backend-outage cases passed through the API and browser; the healthy console had no warnings or errors. One bounded correction cycle made the required `T001` and `T009` identifiers visible beside their trip names. The reviewed replacement screenshots are `evidence/part1-hotel-search.png` and `evidence/part1-hotel-no-results.png`.

The earlier city-search smoke test, screenshots, and local commits were superseded and replaced before publication. The corrected Part 1 checkpoint remains published on `main` at `https://github.com/NateHudson214/hudson-travel`.

On `part2-sqlite-bookings`, the Part 2 implementation now initializes the
ignored SQLite database exactly once, serves hotel search from SQLite, lists
users and joined booking history, and creates, cancels, and deletes persistent
bookings. The Vue interface loads travelers/history, creates a booking for a
displayed trip, cancels while retaining the row, deletes after backend
confirmation, and rereads history after every mutation. Backend tests use
isolated temporary databases and cover all seed IDs,
repeat initialization, SQLite-only search, B007/B008 allocation, persistent
create/cancel/delete behavior, and error responses. Frontend client tests cover
the exact CRUD methods and bodies plus error parsing.

The bounded Part 2 smoke test created B007 for U006/T001, refreshed the browser,
cancelled B007 while retaining it, created B008 for U006/T009, deleted B008,
and then restarted both services. After restart, SQLite contained the six seed
bookings plus cancelled B007; B008 remained absent, and
`next_booking_number=9`. A controlled backend outage displayed a clear booking
error while preserving both search results and booking history. Recovery through
the Vue refresh action succeeded, and the healthy browser console had no warning
or error entries. No source correction cycle was required. The final manual
review passed, the implementation checkpoint was preserved on the remote
feature branch, and the verified non-fast-forward merge was published on
`main`.

For Assignment 2, the fixed ZIP 16802 round trip was observed successfully on
September 23, 2026. The entered-ZIP route, client, form, validation, and result
table are now implemented. Automated verification passed with 57 backend tests,
17 frontend API-client tests, clean Oxlint and ESLint runs, and a successful
20-module production build. No live Geoapify request was made for this
implementation gate. The browser smoke test then observed ZIP 16802 resolving
to State College with coordinates `40.803167822`, `-77.861384958`; verified
leading-zero, loading, validation, sanitized 404/502, hotel-search regression,
and clean-console behavior; and required no source correction. The successful
table was recreated once through a local-only mock using the already-observed
live values so it could remain visible for manual evidence capture without
another intentional provider call. The student subsequently captured and
reviewed the live-results screenshot, synchronized-selection screenshot,
validation screenshot, and demonstration recording. All four repository
evidence files are readable and contain no reported key, secret, private, or
unrelated content. The student then completed the final VS Code review and
confirmed that all visible changes were intentional, protected and generated
files were excluded, and no shortlist or Part 2 behavior was present. The
remaining task is the Assignment 2 Part 1 Canvas submission.

The Assignment 2 Part 1 implementation and evidence checkpoint is
[`0f38ae0ac35808e332ec91472bb0d5393e5adfc8`](https://github.com/NateHudson214/hudson-travel/commit/0f38ae0ac35808e332ec91472bb0d5393e5adfc8).
It is preserved on the published `assignment2-part1-live-hotels` feature
branch. The non-fast-forward merge into `main` is
[`6739c4e5b4e4a93b74d6558253078024b1aa7cbf`](https://github.com/NateHudson214/hudson-travel/commit/6739c4e5b4e4a93b74d6558253078024b1aa7cbf).
The complete automated gate passed both before the feature commit and after the
merge. Assignment 1 checkpoints remain in the same history.
