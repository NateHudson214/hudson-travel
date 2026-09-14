# Major Part 2 SQLite-Booking Prompts

## Backend SQLite and booking CRUD slice

The first Part 2 implementation prompt required a dependency-free backend using
Python's built-in `sqlite3`. It specified an ignored development database at
`backend/instance/hudson_travel.sqlite3`, a focused database module, foreign
keys on every connection, and `hotels`, `trips`, `users`, `bookings`, and
`app_metadata` tables.

The prompt required a one-time, all-or-nothing seed from all four UTF-8-sig CSV
files. Every supplied ID had to be preserved. A durable `csv_seed_version`
marker—not row counts or record existence—had to prevent future reseeding. New
booking IDs had to use a durable counter inside `BEGIN IMMEDIATE`, start at
`B007`, and never be reused after cancellation or deletion.

It also specified these contracts:

> Keep hotel-name search but read it exclusively from SQLite after
> initialization. Add traveler and joined-history reads, create confirmed
> bookings with backend-assigned IDs and dates, cancel while retaining the
> record, and delete with HTTP 204. Test initialization, persistence, monotonic
> IDs, invalid references, missing bookings, and preserved Part 1 behavior with
> temporary database files.

## Vue frontend CRUD slice

The next prompt required the smallest complete Vue interface for every CRUD
action while preserving hotel-name search:

> Load travelers and booking history on startup. Let the user choose a supplied
> traveler and a trip from the current search results, then create a booking
> through FastAPI. Display joined history with booking, traveler, trip, hotel,
> stay dates, booked-on date, and status. Cancel confirmed bookings while
> retaining them, delete a test booking only after backend confirmation, and
> refresh history after every mutation so SQLite remains the source of truth.

The interface prompt also required independent search and booking error state,
disabled conflicting controls during requests, clear validation/loading/
success/error/empty feedback, a focused booking API module, and client tests for
all methods, exact JSON bodies, HTTP details, and empty or malformed errors.

## Scope and verification boundaries

Both prompts prohibited dependency changes, CSV edits, commits, pushes, merges,
and Part 2 scope beyond SQLite booking CRUD. The source gate includes backend
pytest, all frontend API-client tests, Oxlint, ESLint without auto-fix, the Vite
production build, `git diff --check`, protected-file hashes, and database-ignore
checks.

The frontend implementation prompt explicitly deferred the destructive browser
CRUD and process-restart persistence smoke test. No browser or restart result is
considered verified until that bounded follow-up is performed and its observed
results are recorded.
