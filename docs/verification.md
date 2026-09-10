# Part 1 Verification

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
