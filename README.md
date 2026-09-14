# Hudson Travel

Hudson Travel is a small Vue and FastAPI application for searching offered
stays by hotel name and managing simulated bookings. Part 1 provides the hotel
search. The current Part 2 feature-branch work seeds SQLite and provides
frontend-driven booking creation, history, cancellation, and deletion.

The source CSV files in `backend/data/` are read-only seed inputs.

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

The API is available at <http://127.0.0.1:8000>. On first startup it creates
`backend/instance/hudson_travel.sqlite3`, creates the relational schema, and
seeds all four supplied CSVs in one transaction. Later startups use the saved
database without reloading deleted or changed seed records. The `instance/`
directory is ignored by Git.

Search with a request such as:

```text
GET http://127.0.0.1:8000/api/trips?hotel_name=Harbor%20Lantern%20Hotel
```

Interactive API documentation is available at <http://127.0.0.1:8000/docs>.

The implemented Part 2 backend endpoints are:

```text
GET    /api/users
GET    /api/bookings
POST   /api/bookings
PATCH  /api/bookings/{booking_id}
DELETE /api/bookings/{booking_id}
```

`POST /api/bookings` accepts `user_id` and `trip_id`; the backend assigns the
booking ID, booking date, and initial `confirmed` status. Cancellation retains
the record with `cancelled` status, while deletion permanently removes it.

## Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` requests to the backend at
port 8000 during development. Search for a hotel, choose a traveler and one of
the displayed offered stays, and use **Create booking**. The booking-history
table is loaded from SQLite and provides **Cancel**, **Delete**, and **Refresh
history** actions. Cancelled records remain visible; deleted records disappear
only after the backend confirms deletion and history is reloaded.

## Verification

After both environments are prepared, run the automated checks documented in
`docs/verification.md`. The current checks cover:

- `Harbor Lantern Hotel` returns its two offered stays.
- Lowercase, surrounding-space, and partial `Lantern` searches return the same
  two stays.
- `Not a Real Hotel` returns an empty list and a clear no-results message.
- A blank hotel name produces a clear validation error and clears stale results.
- Exact one-time seed counts and IDs.
- Persistent creation, cancellation, and deletion using temporary test
  databases.
- Monotonic booking IDs that are not reused after deletion.
- Frontend clients for loading travelers/history and sending the exact create,
  cancel, and delete requests.

Dependencies belong only in the project-local ignored directories
`backend/.venv/` and `frontend/node_modules/`. The development SQLite file also
remains local and ignored. The automated source checks, frontend-driven browser
CRUD, browser refresh, controlled failure, and full process-restart persistence
checks passed on September 14, 2026.
