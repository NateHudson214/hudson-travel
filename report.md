# Hudson Travel — Part 1 Report

**Assignment:** Part 1 Hotel Search

**Due:** Friday, September 11, 2026, at 11:59 PM ET

**Repository URL:** [https://github.com/NateHudson214/hudson-travel](https://github.com/NateHudson214/hudson-travel)

**Exact Part 1 implementation/evidence checkpoint:**
[`d224428019dd6fb7223c4e607aabc108af145577`](https://github.com/NateHudson214/hudson-travel/commit/d224428019dd6fb7223c4e607aabc108af145577)

## Project context

Hudson Travel is a local educational application built with Vue, FastAPI, and
the instructor-supplied CSV data. Part 1 searches hotels by name and displays
their available fixed-date stays. It does not create real reservations, process
payments, use SQLite, or implement Part 2 booking behavior.

The implementation follows [`docs/design.md`](docs/design.md) and the checks in
[`docs/verification.md`](docs/verification.md).

## Responsibilities

### Interface

Vue provides a labeled hotel-name input and Search button. It displays loading,
validation, request-error, result-summary, no-results, and results-table states.
The table identifies the matching hotel and every associated offered stay.
Validation and request failures remove stale results.

### Logic

FastAPI provides `GET /api/trips?hotel_name={hotel_name}`. Python trims and
validates the query, matches hotel names case-insensitively with partial-name
support, joins trips to matching hotels through `hotel_id`, and returns only the
fields needed by the table.

### Data

Part 1 reads `backend/data/hotels.csv` and `backend/data/trips.csv` with
`encoding="utf-8-sig"`. The supplied CSV files are read-only. `users.csv` and
`bookings.csv` remain preserved for the later assignment but are unused here.

## Expected versus observed verification

| Check | Expected | Observed |
| --- | --- | --- |
| Backend tests | Exact, normalized, partial, unmatched, missing, and blank searches pass | 6 passed; two non-failing dependency warnings |
| Frontend tests | Correct parameter encoding and friendly error handling pass | 3 passed |
| Frontend lint/build | No findings and successful production build | Both linters passed; Vite transformed 14 modules |
| `Harbor Lantern Hotel` | `T001` and `T009` | Passed; table showed both IDs, trip names, hotel, Boston, MA, dates, and $150 rate |
| Lowercase and surrounding spaces | Same two stays | Passed; both forms returned the same two rows |
| `Lantern` | Same two stays through partial matching | Passed; displayed T001 and T009 |
| `Not a Real Hotel` | Clear no-results message and no table | Passed; message displayed and table was absent |
| Blank hotel name | Clear validation and no stale table | Passed after a successful search; validation displayed and both rows/table cleared |
| Backend unavailable | Friendly request error and no stale table | Passed by stopping only the test backend; request error displayed and prior rows/table cleared |
| Healthy browser console | No application errors | Passed; no warnings or errors were reported |
| Protected files | CSV and dependency declarations unchanged | SHA-256 values match the pre-correction values |

The previous city-search implementation, smoke evidence, screenshots, and local
commit hashes were based on a superseded interpretation and are not final Part 1
evidence. No remote was created, so that work was never published.

## Evidence

- Successful hotel search: [`evidence/part1-hotel-search.png`](evidence/part1-hotel-search.png), reviewed and readable.
- Unmatched hotel search: [`evidence/part1-hotel-no-results.png`](evidence/part1-hotel-no-results.png), reviewed and readable.
- Corrected manual VS Code scan: completed by the student; all visible changes
  were intentional, no secrets or `.env` files were present, generated output
  was excluded, and the source CSV files were unmodified.
- Public repository and clickable implementation commit links are recorded
  above; `main` was pushed to GitHub after verification.

Capture instructions are in [`evidence/README.md`](evidence/README.md), the
prompt record is in
[`prompts/001-part1-hotel-search.md`](prompts/001-part1-hotel-search.md), and
the current state is in [`handoffs/current.md`](handoffs/current.md).

## Part 2 boundary

Part 2 has not started. No database, persistence, traveler selection, or booking
CRUD belongs in this checkpoint.
