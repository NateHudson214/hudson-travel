# Hudson Travel — Assignment 1 Design

**Status:** The Part 1 CSV-backed search has been corrected to use hotel name, as required by the authoritative assignment table. The corrected automated gate and API/browser smoke test pass, both replacement screenshots have been reviewed at their required repository paths, and the student completed the final VS Code review. The corrected implementation/evidence checkpoint is `d224428019dd6fb7223c4e607aabc108af145577`. The two earlier local commits and their city-search evidence were replaced before publication. Creating the remote and pushing remain pending. Part 2 has not started.

## Design revision

The detailed checkpoint instructions materially replace parts of the earlier plan. Part 1 is now a working CSV-backed search checkpoint rather than planning only. The custom six-hotel catalog and JSON booking store are removed. Hudson Travel will use the instructor's records and fixed trip dates. Part 2 will seed SQLite once from all four CSV files and provide booking CRUD through the Vue interface, including cancellation and deletion. These changes are required by the updated assignment rather than optional scope growth.

## Application scope

Hudson Travel adapts the course calculator project into a small local hotel application with a Vue frontend, a Python backend, and FastAPI communication between them. Part 1 lets a user search by hotel name and displays that hotel's matching offered stays from joined hotel/trip records in a plain table. Part 2 moves the supplied data into SQLite and adds simulated booking history with create, read, cancel, and delete actions. All identities, trips, and bookings are synthetic; the application does not connect to Expedia or perform real purchases.

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
| Interface | Vue provides a hotel-name input, Search button, result table, loading/error feedback, and no-results message. | Vue adds booking creation, history, cancellation, and test-booking deletion controls. Every CRUD action is initiated in the frontend. |
| Logic | Python trims and validates the hotel-name query, performs case-insensitive partial matching, joins trips to hotels through `hotel_id`, and returns predictable results. | Python validates user/trip references, assigns unique booking IDs, permits valid status changes, and controls deletion. |
| Data | `hotels.csv` and `trips.csv` are read-only sources. Trips have fixed dates and are the rows returned by search. | All four CSVs seed relational SQLite tables once. After seeding, reads and writes use SQLite only. |
| Persistence | No user-created state is required. Search data comes from the supplied CSV files whenever the backend runs. | SQLite preserves additions, cancellations, and deletions across browser refresh and frontend/backend restarts without duplicating or restoring seed records. |

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

On the first run only, create SQLite tables for hotels, trips, users, and bookings and seed them from the four supplied CSVs while preserving every provided ID. A durable initialization marker or equivalent one-time strategy must prevent reseeding on later starts. Checking only whether an individual row exists is insufficient because deleting a seeded test booking must not cause that booking to reappear after restart.

After initialization, every application read and write uses SQLite rather than rereading CSV files. The database file is local application state and must survive frontend/backend restarts.

### Required frontend-driven CRUD

- **Create:** Select a supplied demo traveler and offered trip, then create a booking with a new unique booking ID.
- **Read:** Display seeded and newly created bookings in history, including connected traveler, trip, and hotel information.
- **Update:** Cancel a booking by changing its status to `cancelled` while retaining the record.
- **Delete:** Delete a chosen test booking through an explicit frontend action.

The frontend must send each operation through FastAPI to Python; it must not mutate a local-only booking list.

### Likely API surface for Part 2

```text
GET    /api/trips?hotel_name={hotel_name}
GET    /api/users
GET    /api/bookings
GET    /api/bookings/{booking_id}
POST   /api/bookings
PATCH  /api/bookings/{booking_id}
DELETE /api/bookings/{booking_id}
```

Exact request and response shapes will be finalized before Part 2 implementation.

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

The earlier city-search smoke test, screenshots, and local commits were superseded and replaced locally. The student completed the corrected manual VS Code scan and confirmed that the visible changes are intentional, no secrets or `.env` files are present, generated dependencies and build output are excluded, and the source CSV files are unmodified. The corrected implementation/evidence checkpoint is `d224428019dd6fb7223c4e607aabc108af145577`. No remote has been created and Part 2 has not started.
