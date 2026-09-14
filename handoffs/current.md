# Current Handoff

**Updated:** September 14, 2026

**Checkpoint:** Part 1 preserved; Part 2 verified, merged, and published

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

Upload `report.md` to the Part 2 Canvas assignment and confirm the submitted
file is the updated Part 2 report. Do not make further source changes unless a
submission review identifies a specific issue.

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
