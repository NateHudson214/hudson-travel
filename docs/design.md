# Hudson Travel — Project Design

**Status:** Assignment 1, Assignment 2 Part 1, and the additive local-hotel
storage checkpoint remain preserved and published. Assignment 2 Part 2 chatbot
work continues on `assignment2-part2-rag-chatbot`. Research, early design,
backend-only configuration, safe health reporting, preserved OpenRouter
compatibility, and a mocked two-request OpenAI client are implemented. The
read-only SQL boundary and durable advisor history are verified with temporary
databases, and `POST /api/hotel-advisor` orchestrates both model stages around
that boundary. The Vue advisor interface has now completed a bounded
visible-browser workflow using deterministic local-only provider mocks and a
temporary database, including refresh and service-restart persistence. A
controlled live request then completed both OpenAI stages, read-only retrieval,
and durable refresh/restart restoration. The model bound an otherwise yearless
October question to 2024 rather than the stored 2026 demo dates, so the live
result was a truthful no-match rather than the intended matching answer. The
versioned prompt now contains a focused 2026 yearless-date rule. A single live
rerun used 2026 and completed both stages, but interpreted "through October 12"
as checkout October 13 and produced an incorrect decimal total. The run was not
accepted as grounded-answer evidence and was not retried.

The focused follow-up retains the public endpoint shape while tightening the
internal provider contract. Total-cost retrieval returns integer
`total_cost_cents`; the provider returns that integer with a single
`{{total_cost}}` marker rather than formatting currency. The provider-neutral
route boundary accepts only a retrieved total and renders dollars itself by
dividing cents by 100 with two decimal places. It also rejects provider-written
dollar text whenever a structured retrieved total is available. Mocked coverage
now proves the required October 10 inclusive/October 12 exclusive boundary and
the deterministic `$200.00` rendering. Live verification remains pending.

The next single authorized live attempt stopped at the existing SQL boundary:
the proposal was rejected as unsafe before local retrieval or the grounded
answer stage. The sanitized HTTP 422 result persisted as a failed audit run.
No retry or design change was made during that demonstration.

The subsequent read-only diagnostic found a compound `UNION` and three joins.
Both violate the existing validator, so the rejection was correct and the
validator remains unchanged. The smallest correction is prompt-only: the
demonstration proposal must be one flat `SELECT`, use exactly two joins across
the three approved tables, bind the October 10 inclusive/October 12 exclusive
range, group once, and return the requested-night, minimum-room, and integer-
cent aggregates. Mocked tests covered this shape before the final live run.

The final authorized live run on October 9, 2026 validated that design. Its
single flat query used exactly two joins, only the three allowed tables, and the
required date boundary. The accepted read-only result contained Hotel State
College, two nights, 20 minimum rooms, and 20000 cents; deterministic backend
formatting produced `$200.00`. The completed conversation and answer persisted
through browser refresh and full service restart without provider replay.
The read-only history contract now includes an optional
`latest_completed_run` with only status, proposed SQL, structured parameters,
retrieved records, run ID, and prompt version. Vue combines that object with the
persisted assistant message to restore the full evidence panel. Failed and
pending runs, executed SQL, provider details, hidden prompts, errors, and
database paths remain excluded.

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

## Assignment 2 Part 2 — grounded hotel advisor

The authoritative Part 2 endpoint adds a natural-language advisor over only
the locally saved provider hotels, saved search associations, and clearly
labeled simulated nightly rates and availability. The newly prioritized
provider is OpenAI with `gpt-6-luna`; the earlier OpenRouter/Nemotron client is
preserved while the backend moves shared contracts behind provider-neutral
types. Provider availability, limits, model routing, and pricing can change and
are not application guarantees.

The smallest design uses one `POST /api/hotel-advisor` endpoint. The first
backend-only model request receives the question, the exact three-table schema,
and strict query rules, and must propose a parameterized query through a forced
tool call. The backend then validates the proposal through layered controls and
executes it with a read-only SQLite URI, query-only mode, a restrictive
authorizer, bound parameters, progress and row limits, and sanitized errors.
Only after successful retrieval does a second backend-only request receive the
original question, accepted query and parameters, and bounded records to
produce a grounded answer. Vue will display the question, proposed SQL,
retrieved records, answer, and a clear answered, no-match, or
insufficient-data status.

The complete official-source research, provider limitations, schema boundary,
security controls, provisional API shape, and test strategy are recorded in
[`docs/assignment2-part2-rag-research.md`](assignment2-part2-rag-research.md).
The explicitly unimplemented early interface is
[`docs/mockups/assignment2-part2-rag-early.svg`](mockups/assignment2-part2-rag-early.svg).
The frozen Part 1 list/map behavior, local-first lookup, Add/Remove workflow,
persistence, Assignment 1 records, and attribution remain unchanged.

### Implemented provider client boundaries

The route-independent backend client now provides two separately callable
operations. `propose_hotel_query` sends the question with only the approved
three-table schema and forces exactly one tool call containing SQL and bound
parameters. The returned proposal is explicitly untrusted and is not executed.
`generate_grounded_answer` sends the original question, an already accepted
query and parameters, and bounded retrieved records with instructions to use no
other facts and to label the nightly data as simulated. It forces one strict
`return_grounded_answer` tool result containing only `status` and `answer`.
Local checks reject `answered` for an empty result and `no_matches` for a
nonempty result; `insufficient_data` remains available when required data is
missing.

Both operations use backend-only configuration, a finite timeout, deterministic
temperature, bounded output tokens, and injectable HTTP behavior. Focused
internal exceptions distinguish missing configuration, authentication,
quota/rate limiting, unavailable model, transport, other provider HTTP, and
malformed-response failures without surfacing credentials or raw provider
details. The contract is verified only with mocked responses; live OpenRouter
success remains unverified.

Shared query, answer, and sanitized failure contracts now live outside either
provider client. Existing OpenRouter exception types remain compatibility
subclasses so its existing client and tests continue to behave unchanged. The OpenAI
Responses client reads only backend configuration, loads the repository prompt
from `prompts/hotel-assistant.md`, includes its deterministic SHA-256 version,
sets `store: false`, and forces one strict function result per stage. Named SQL
parameters use a strict array of name/value objects on the provider boundary
and are converted to the shared dictionary contract before validation.

The OpenAI client is now the route default. Application-state providers supply
the backend key, model, prompt loader, and an optional per-call HTTP transport;
production owns and closes its clients while tests return fresh
`MockTransport` instances. Its exact endpoint, method, model, headers, timeout,
payload, function schemas, parsing, status consistency, and sanitized error
categories are covered without a live OpenAI request.

### Implemented read-only SQL boundary

The query layer validates an untrusted proposal before opening SQLite. It
accepts only one bounded, named-parameter `SELECT` or non-recursive
`WITH ... SELECT`; limits SQL and parameters; rejects comments, multiple
statements, writes, schema operations, PRAGMAs, attach/detach, transactions,
recursive or compound queries, unrelated tables, table reuse, excessive joins,
and unbounded output; and requires parameter names to match placeholders.

For execution it opens only the explicitly supplied path with SQLite URI
`mode=ro`, applies `query_only` and `trusted_schema=OFF`, and then installs a
deny-by-default authorizer. The authorizer allows reads only from documented
columns in `saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`, plus
a minimal aggregate/scalar function set. A progress handler, 50-row fetch cap,
text-cell limit, serialized-size limit, and scalar conversion checks bound the
result. All errors are sanitized. Temporary-database tests prove multi-night
inclusive-check-in/exclusive-checkout retrieval, integer-cent totals, leading
zero preservation, honest nulls, parameter binding, adversarial rejection, and
record preservation.

### Implemented mocked orchestration endpoint

`POST /api/hotel-advisor` accepts a JSON `question`, trims it, and rejects a
missing, blank, non-string, or over-500-character value before any workflow
stage. Injectable application-state callables run proposal, read-only retrieval,
and grounded answer exactly in that order. The retrieval receives the
application database path and exact proposal; the second request receives the
normalized original question, accepted SQL, exact parameters, and exact bounded
records.

Only a fully successful workflow returns the grading evidence fields plus
conversation, message, run, and prompt-version identifiers. An empty valid
result still reaches the second model stage. Rejected/excessive
queries stop before the second call and map to 422; database failures map to
500; missing configuration maps to 503; quota/rate limiting maps to 429; and
other provider or malformed responses map to a sanitized 502. Mocked route
tests cover stage order, arguments, all statuses, early stops, and error
sanitization without live provider traffic or development-database mutation.
An additional end-to-end mocked test uses the route defaults, two mocked OpenAI
Responses calls, and actual bounded retrieval from a temporary SQLite database.
It proves that an unsafe proposal stops before the second provider call and
that safe provider failures retain the documented HTTP mappings.

### Implemented advisor persistence boundary

Three additive tables record durable advisor state without changing the saved
hotel schema. `advisor_conversations` owns created/updated timestamps;
`advisor_messages` stores ordered user/assistant content; and `advisor_runs`
stores the prompt version, normalized question, proposed and executed SQL,
JSON-encoded bound parameters and bounded records, final status, and only a
safe failure category/message. Foreign keys connect every message and run to
its conversation. CHECK and UNIQUE constraints restrict roles, statuses, and
message order.

Durable `C`, `M`, and `R` identifiers come from independent metadata counters
advanced inside `BEGIN IMMEDIATE` transactions, so failed or removed history
cannot cause reuse. The route opens separate short transactions before the
first provider call, after proposal, after retrieval, and after the answer; no
provider wait holds a write lock. A failed stage updates its pending run with a
safe failure record when storage remains available.

The request accepts an optional `conversation_id`. A known ID supplies the 12
most recent ordered user/assistant messages to both OpenAI stages; an unknown ID
returns 404 before provider access. Successful responses add conversation,
message, run, and prompt-version identifiers while preserving all grading
fields. Two bounded read-only endpoints expose only user-visible summaries and
messages. Temporary-database and mocked-provider tests verify this design; the
ignored development database and live provider remain untouched.

### Implemented Vue conversation interface

`HotelAdvisor.vue` owns only advisor state. It loads bounded summaries, reopens
the latest conversation after page load, starts a new conversation without
deleting history, and sends the active ID for follow-up questions. After a
successful POST it retains the returned evidence, rereads the conversation from
SQLite, and refreshes the summaries. A browser refresh can therefore reconstruct
visible history from the backend instead of browser-only storage.

The panel renders ordered user/assistant messages, all grading evidence, and
explicit answered, no-match, and insufficient-data states. Invalid questions,
unknown history, SQL rejection, configuration, rate-limit, provider, retrieval,
and history failures use safe messages. Existing valid messages remain visible
after a failed follow-up, while stale SQL/record/answer evidence is cleared. No
state is shared with the existing travel workflows. The October 8, 2026
bounded browser check used the normal local routes, SQL validator, read-only
executor, persistence layer, and Vue client with deterministic provider mocks.
It verified loading/disabled controls, exact evidence rendering, ordered
follow-ups, new and reopened conversations, refresh and full-service restart
persistence, safe 404/422/429/500/502/503 states, travel-workflow isolation,
and a clean console. After the local API-key typo was corrected, the later
controlled live attempt completed both provider stages and returned HTTP 200.
Run `R000004` used only the three approved tables through the read-only
validator/executor and persisted conversation `C000002`. Its parameters were
`checkin=2024-10-10` and `checkout=2024-10-12`, so retrieval returned no rows
and the second stage produced a consistent, simulated-data-labeled no-match
answer. Refresh and full service restart restored the conversation without a
new provider request. The focused prompt correction now states that the course
data covers October 10–14, 2026 and that yearless October ranges must bind to
2026 without inventing another year. Mocked regression coverage passes. The
next live proposal used 2026, but chose checkout October 13 and the second stage
reported $32.55 even though its three retrieved nightly values totaled $325.50.
This exposes separate date-boundary and arithmetic-grounding defects; the
intended live demonstration remains unverified.

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

## Assignment 2 Part 2 in-class local-hotel workflow

This additive workflow does not merge Geoapify hotels into the instructor
`hotels` table. Provider records use their exact `place_id` in `saved_hotels`.
`saved_hotel_searches` connects each provider hotel to a searched five-digit ZIP
and stores the resolved postcode, country code, coordinates, and optional
locality. Its composite `(hotel_id, zip_code)` key prevents duplicate
associations while allowing many hotels per ZIP and one hotel under multiple
ZIP searches.

`demo_hotel_nights` keeps one row per saved hotel and date. Saving creates the
five dates from October 10 through October 14, 2026 in the same transaction as
the hotel and search association. SQLite defaults supply `10000` cents and 20
rooms. `INSERT OR IGNORE` makes the save repeatable without overwriting a rate
or room count changed later in DB Browser. Foreign-key cascades let one removal
transaction delete the selected provider hotel, its associations, and nights
while leaving unrelated provider and Assignment 1 records intact.

The additive API contract is:

```text
GET    /api/saved-hotels/ids
GET    /api/saved-hotels?zip_code={zip_code}
POST   /api/saved-hotels
DELETE /api/saved-hotels/{provider_place_id}
```

The ZIP collection route uses the same trimmed, five-ASCII-digit validation as
the live search. It returns stored location context, provider identity/location
fields, and ordered demo nights. A valid ZIP without saved matches is a normal
HTTP 200 empty result. SQLite failures map to a safe HTTP 500 and are never
treated as permission to call Geoapify.

The Vue nearby-hotel flow now reads saved IDs on page load and checks the local
ZIP collection before live search. A nonempty local result is labeled **Saved
locally**, is explicitly described as an incomplete saved subset, includes the
simulated dates/rates/rooms, and makes no provider request. Only a successful
empty local result falls through to the existing live endpoint, labeled **API
results**. Add and Remove state changes occur only after FastAPI confirms them.
The existing `selectedPlaceId` continues to synchronize keyboard-accessible
list choices and Leaflet markers for both sources.

Temporary-database and frontend API-client checks cover the implemented
contract. The bounded October 1, 2026 browser check then used one live ZIP
`16802` request, saved two provider hotels, proved the local-first short circuit,
and displayed the saved subset after refresh. The student changed Hotel State
College's October 12 row to 12,550 cents and 7 rooms in DB Browser; Vue displayed
`$125.50` and 7, and both values survived a complete backend/frontend restart.
Removing Scholar Hotel State College through Vue returned HTTP 204 and removed
only that hotel, association, and five nights.

One correction cycle addressed keyboard marker selection: Leaflet keyboard
activation had opened a popup without updating the shared list selection. The
marker now forwards both click and keypress selection to the parent. The full
automated gate passed after the correction, and saved-result list-to-map and
map-to-list keyboard synchronization then passed visibly.

The reviewed repository evidence preserves three complementary views of this
workflow: the saved-local interface with the edited `$125.50`/7-room row, the
Safari Network panel showing the local saved-hotels request without a live
nearby-hotels request, and the five persisted SQLite night rows. These captures
are documentation evidence only; the ignored development database remains the
source of the local verification state and is not intended for Git.

The reviewed implementation and evidence checkpoint is
[`77ae9b397caf3a3062d1ae8955aaf30cd0d1456d`](https://github.com/NateHudson214/hudson-travel/commit/77ae9b397caf3a3062d1ae8955aaf30cd0d1456d).
It was published on `assignment2_part2_in_class`, merged into `main` at
[`79e0b6ddd0acb1909059ef344d1bc369f78fe25e`](https://github.com/NateHudson214/hudson-travel/commit/79e0b6ddd0acb1909059ef344d1bc369f78fe25e),
and the complete automated and integrity gate passed on both the feature branch
and merged `main`. The final manual VS Code review also passed before the
checkpoint was created.

## Assignment 2 Part 2 chatbot checkpoint

The reviewed implementation/evidence commit is
[`acdd832c1a78c0351238ca18f1c54bb6b90340b7`](https://github.com/NateHudson214/hudson-travel/commit/acdd832c1a78c0351238ca18f1c54bb6b90340b7),
and its non-fast-forward `main` merge is
[`6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef`](https://github.com/NateHudson214/hudson-travel/commit/6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef).
The final manual review passed. Both the feature branch and merged `main` passed
the complete verification and integrity gate. The published checkpoint keeps
the earlier Assignment 1, Assignment 2 Part 1, and local-hotel history intact;
Canvas submission remains manual.
