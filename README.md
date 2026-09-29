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

Hudson Travel reads the Geoapify credential from `.env` in the project root.
Create that local file from the key-free `.env.example`, then set:

```text
GEOAPIFY_API_KEY=your-local-key
```

The credential is loaded only by the Python backend and must not be placed in
Vue code or a `VITE_` variable. The local `.env` file is ignored by Git. Restart
the backend after creating `.env` or changing its value. The safe
`GET /api/health` response reports only whether the key is configured and never
returns the credential.

The backend Geoapify controller resolves a supplied U.S. postcode through the
Forward Geocoding API. It sends the structured `postcode`, `type=postcode`,
`filter=countrycode:us`, and `format=json` parameters with a finite timeout. A
usable result must match the requested postcode and U.S. country code and
contain valid latitude and longitude coordinates. The internal result contains
only the postcode, country code, coordinates, and an available locality. Missing
configuration, an unresolved postcode, and provider failures remain distinct
sanitized errors. `GET /api/demo/zip-location` calls this controller with the
fixed demonstration ZIP `16802` and returns only the small location response.
Missing configuration returns HTTP 503, an unresolved ZIP returns HTTP 404, and
a provider failure returns HTTP 502 without exposing credentials or raw provider
details.

The graded entered-ZIP extension adds:

```text
GET /api/zip-location?zip_code={zip_code}
```

The route treats the ZIP as text, trims surrounding whitespace, and requires
exactly five ASCII digits so values such as `02113` keep their leading zero.
Missing or invalid input returns HTTP 400. Valid requests use the same backend
controller and sanitized 404, 503, and 502 mappings as the fixed demonstration.

Assignment 2 Part 1 adds the backend hotel-search contract:

```text
GET /api/hotels/nearby?zip_code={zip_code}
```

The route validates and resolves the exact U.S. ZIP, then asks Geoapify Places
for up to 20 `accommodation.hotel` features inside a strict 5,000-metre circle
around the returned point. The backend returns the resolved location,
`radius_meters`, `result_limit`, and sanitized hotel records containing the
provider place ID, optional name and formatted address, coordinates, and
optional distance. A successful search with no usable hotels returns HTTP 200
with an empty `hotels` array. Invalid ZIP, unresolved ZIP, missing
configuration, and provider failures remain distinct safe 400, 404, 503, and
502 responses. No key or provider URL is returned to Vue.

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
port 8000 during development. The **ZIP lookup demonstration** panel sends
`GET /api/demo/zip-location` only to FastAPI and displays the fixed ZIP 16802
location without placing the Geoapify credential in Vue. The same panel also
accepts an entered five-digit ZIP as text, validates it locally, sends it to
`GET /api/zip-location`, and displays the returned location in a plain table.
Invalid or failed entered-ZIP lookups clear stale dynamic results and show clear
feedback. The Part 1 nearby-hotel interface uses a separate five-digit ZIP
search, calls only the local combined FastAPI endpoint, and displays the
resolved center with a provider-derived hotel list and Leaflet map. The list
and markers share one selected provider place ID. Missing provider fields use
honest fallbacks, while validation, unresolved ZIP, empty results, and service
failures remain distinct. Leaflet uses standard OpenStreetMap tiles with visible
tile attribution, and the results display Geoapify attribution. This frontend
slice passed automated tests, lint, build, one bounded live Places/browser
smoke test, synchronized list/map selection checks, safe local-only state
checks, and final evidence review on September 29, 2026. Shortlist behavior
remains outside Part 1.
Search for a hotel,
choose a traveler and one of the displayed offered stays, and use **Create
booking**. The booking-history table is loaded from SQLite and provides
**Cancel**, **Delete**, and **Refresh history** actions. Cancelled records remain
visible; deleted records disappear only after the backend confirms deletion and
history is reloaded.

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
