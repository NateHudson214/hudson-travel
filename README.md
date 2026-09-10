# Hudson Travel

Hudson Travel is a small Vue and FastAPI application for searching offered
stays by hotel name. Part 1 reads instructor-supplied hotel and trip records
from CSV files, joins them by `hotel_id`, and displays matching fixed-date stays.

This checkpoint does not create bookings or use a database. The source CSV
files in `backend/data/` are read-only project inputs.

## Prerequisites

- Python 3.11 or newer
- Node.js ^22.18.0 or >=24.12.0
- npm

## Backend setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

The API is available at <http://127.0.0.1:8000>. Search with a request such as:

```text
GET http://127.0.0.1:8000/api/trips?hotel_name=Harbor%20Lantern%20Hotel
```

Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

## Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` requests to the backend at
port 8000 during development.

## Verification

After both environments are prepared, run the automated checks documented in
`docs/verification.md`. The main acceptance cases are:

- `Harbor Lantern Hotel` returns its two offered stays.
- Lowercase, surrounding-space, and partial `Lantern` searches return the same
  two stays.
- `Not a Real Hotel` returns an empty list and a clear no-results message.
- A blank hotel name produces a clear validation error and clears stale results.

Dependencies belong only in the project-local ignored directories
`backend/.venv/` and `frontend/node_modules/`.
