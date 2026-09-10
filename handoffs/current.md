# Current Handoff

**Updated:** September 10, 2026

**Checkpoint:** Corrected Part 1 hotel-name search verified, reviewed, committed, and pushed

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
- No Part 2 behavior has started.

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
- Canvas submission of `report.md` remains a manual student action.

## Next action

Upload `report.md` to the Part 1 Canvas assignment and confirm submission before
starting any Part 2 work.
