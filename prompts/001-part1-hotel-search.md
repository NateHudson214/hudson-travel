# Major Part 1 Hotel-Search Prompts

## Authoritative correction

The authoritative assignment table requires a hotel-name search input and a
Search button. Results must display matching hotels and their available stays
from `hotels.csv` and `trips.csv`, joined through `hotel_id`, with a clear
no-results state. Verification must include a supplied hotel name, an unmatched
search, a manual VS Code scan, a pushed Git checkpoint, and recorded expected
versus observed results.

The correction prompt required the smallest Part 1-only change:

> Change the API search parameter from `city` to `hotel_name`. Trim the hotel
> name, match it case-insensitively, prefer partial-name support, and return every
> offered stay associated with matching hotels. Use `Harbor Lantern Hotel` as
> the primary successful case (`T001` and `T009`) and `Not a Real Hotel` for the
> no-results case. Update the Vue interface, tests, documentation, handoff,
> report, prompt record, and screenshot instructions. Do not start Part 2 or
> publish until the corrected work is verified.

## Superseded interpretation

The earlier implementation prompt used city search because the initial design
document incorrectly treated city as the Part 1 search criterion. Its useful
constraints remain: preserve the Vue/Vite/FastAPI configuration, read CSV files
with `utf-8-sig`, join through `hotel_id`, keep supplied CSVs unchanged, clear
stale results, distinguish no-results from request failures, test behavior, and
avoid all Part 2 work. The city criterion and its evidence are superseded.

## Corrected acceptance cases

- `Harbor Lantern Hotel` → `T001` and `T009`.
- Lowercase and surrounding-space variations → the same two stays.
- Partial `Lantern` → the same two stays.
- `Not a Real Hotel` → `200 []` and a clear no-results state.
- Blank input → clear validation and no stale results.
- Backend unavailable → friendly request error and no stale results.

## Corrected smoke test and evidence

The follow-up smoke-test prompt required the complete automated gate, protected
hash checks, API verification through the frontend proxy, every corrected
browser case, stale-result and safe network-failure checks, and a clean browser
console. AutoLoop was limited to five correction cycles. The observed run used
one cycle to make T001 and T009 visible in the results table, then passed all
checks. The prompt required the two replacement screenshots to be captured and
reviewed before the corrected Git checkpoint.
