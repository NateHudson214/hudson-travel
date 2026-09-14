# Hudson Travel — Part 2 Report Draft

**Assignment:** Part 2 SQLite Booking CRUD

**Due:** Tuesday, September 15, 2026, at 11:59 PM ET

**Repository URL:** [https://github.com/NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel)

**Preserved Part 1 implementation/evidence checkpoint:**
[`d224428019dd6fb7223c4e607aabc108af145577`](https://github.com/NateHudson214/hudson-travel/commit/d224428019dd6fb7223c4e607aabc108af145577)

**Exact Part 2 checkpoint:** `[PLACEHOLDER — add after reviewed feature work is committed and merged]`

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
were unmodified. This report still needs the exact Part 2 checkpoint/merge
commit and final pushed status before upload.

Major implementation instructions are retained in
[`prompts/002-part2-sqlite-bookings.md`](prompts/002-part2-sqlite-bookings.md).
