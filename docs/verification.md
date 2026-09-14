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
