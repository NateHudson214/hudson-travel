# Current Handoff

**Updated:** September 10, 2026

**Checkpoint:** Corrected Part 1 hotel-name search verified and reviewed; Git checkpoint in progress

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

The two existing local commits contain the earlier city-search interpretation.
They were never pushed and must not be identified as the final Part 1 checkpoint.
The obsolete Boston and Seattle screenshots have been removed. A corrected
commit will be created only after automated checks, browser checks, replacement
screenshots, and manual review pass.

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
- Final Part 1 commit hash
- Public GitHub repository URL

## Current limitations

- GitHub CLI authentication was invalid at the last check and must be renewed
  before creating the remote.
- The repository has no remote and nothing has been pushed.
- Local dependencies and build output remain ignored and must not be committed.

## Next action

Replace the superseded local history with the reviewed Part 1 hotel-search
checkpoint, then create the remote and push only after student authorization.
Do not start Part 2.
