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
OPENROUTER_API_KEY=your-local-openrouter-key
OPENROUTER_MODEL=nvidia/nemotron-3.5-lightning:free
OPEN_AI=your-local-openai-key
OPENAI_MODEL=gpt-6-luna
```

All credentials are loaded only by the Python backend and must not be placed
in Vue code or a `VITE_` variable. The local `.env` file is ignored by Git.
Restart the backend after creating `.env` or changing any value. The safe
`GET /api/health` response reports only whether each key is configured and
never returns a credential. It also reports the non-secret OpenRouter and
OpenAI model identifiers. A missing or blank `OPENROUTER_MODEL` uses the
reviewed free default `nvidia/nemotron-3.5-lightning:free`; a missing or blank
`OPENAI_MODEL` uses `gpt-6-luna`. Provider pricing, model availability, quotas,
and rate limits may change. OpenAI configuration and health reporting are now
implemented. After correcting the local `OPEN_AI` value, one controlled live
two-stage request completed on October 8, 2026. The read-only query and grounded
no-match answer were persisted, refreshed, and restored after service restart.
The model supplied 2024 dates for an otherwise yearless question. The versioned
prompt now explicitly defines the October 10–14, 2026 course-data range and
requires 2026 for yearless October date ranges. A single authorized rerun used
2026, but treated "through October 12" as checkout October 13 and returned an
incorrect $32.55 total for records totaling $325.50. That run is persistence
evidence, not final grounded-answer evidence; no retry was made.

The follow-up correction makes the required wording unambiguous: October 12 is
the excluded checkout boundary, so the requested nights are October 10 and 11.
For total-cost queries, SQL returns an integer `total_cost_cents`. The model
returns that same integer plus a `{{total_cost}}` marker; the provider-neutral
route boundary verifies the integer against retrieved records and replaces the
marker using cents divided by exactly 100. A missing, shifted, unsupported, or
free-form dollar amount is rejected safely. This safeguard is verified only
with mocked responses. One later authorized live attempt reached the proposal
stage, where the local validator rejected the proposed query for safety with
HTTP 422. The answer stage did not run, no retry occurred, and no success
evidence was created.

The persisted rejected proposal was diagnosed without execution or provider
traffic. It used a compound `UNION` shape and three joins, both outside the
existing safety boundary. The validator remains unchanged. The repository
prompt now requires the demonstration query to be one flat `SELECT` with no
compound form and exactly two joins across the three approved tables. Mocked
integration coverage verifies the October 10–11 retrieval and backend-grounded
`$200.00` result; at that stage, a corrected live result was still unverified.

One final authorized live run succeeded on October 9, 2026. The model proposed
one flat query with exactly two joins and the required `2026-10-10`/
`2026-10-12` inclusive/exclusive boundary. The validator accepted it, read-only
SQLite retrieval returned Hotel State College with two requested nights, 20
minimum rooms, and `total_cost_cents: 20000`, and the backend rendered the
grounded `$200.00` answer with the simulated-data disclosure. Conversation
`C000005`, messages `M000009` and `M000010`, and run `R000007` survived refresh
and a full service restart without another advisor POST or provider request.
The conversation-detail endpoint now returns the latest completed run's safe
grading fields, so reopening `C000005` also restores its SQL, structured
parameters, retrieved records, status, run ID, prompt version, and persisted
assistant answer. Read-only browser verification passed before and after a full
service restart using GET requests only. The student reviewed and accepted the
two PNGs as submission evidence. The Network image proves GET-only restoration;
the advisor image shows the saved question, `$200.00` answer, and simulated-data
disclosure, while the lower SQL, parameters, record, run ID, and prompt version
remain supported by the recorded browser verification rather than that crop.

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

The Assignment 2 Part 2 in-class local-hotel endpoints are:

```text
GET    /api/saved-hotels/ids
GET    /api/saved-hotels?zip_code={zip_code}
POST   /api/saved-hotels
DELETE /api/saved-hotels/{provider_place_id}
```

`POST /api/saved-hotels` stores one provider hotel together with the searched
ZIP and resolved location context. The provider `place_id` is retained exactly
as the local hotel key; provider name and address remain nullable. The same
transaction creates five simulated classroom nights for October 10–14, 2026.
Their defaults are $100.00 (`10000` cents) and 20 rooms. Repeating a save does
not duplicate rows or overwrite an edited rate or room count. Removing a saved
hotel transactionally removes its ZIP associations and demo nights without
touching Assignment 1 hotel, trip, user, or booking records.

The SQLite additions are `saved_hotels`, `saved_hotel_searches`, and
`demo_hotel_nights`. The association table supports multiple hotels for one ZIP
and multiple ZIPs for one hotel while preventing a duplicate hotel/ZIP pair.
An empty valid local ZIP lookup is HTTP 200 with an empty hotel list; a database
failure remains a clear error and does not trigger a live-provider fallback.

### Assignment 2 Part 2 provider client foundations

The backend has a focused OpenRouter client for the hotel advisor. Its first
function sends a natural-language question with
only the `saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights` schema
and forces one `propose_hotel_query` tool call. It returns an untrusted SQL and
parameter proposal but does not validate or execute it. Its second function
sends an already accepted query, bound parameters, bounded retrieved records,
and the original question through a forced `return_grounded_answer` tool call.
Strictly parsed arguments contain only a status (`answered`, `no_matches`, or
`insufficient_data`) and answer. Local checks reject a status that conflicts
with whether retrieved records exist.

Both functions use the backend-only key, configured model, finite timeouts,
deterministic settings, and bounded output tokens. Authentication, rate-limit,
unavailable-model, transport, provider, and malformed-response failures become
sanitized internal errors. Mocked tests cover the request and response contract;
no live OpenRouter request has been made. The read-only SQL validator and
retrieval layer are implemented separately as described below and are now
wired into the mocked backend endpoint. This client remains available for
compatibility but is no longer the route default.

### Assignment 2 Part 2 read-only retrieval boundary

The advisor query module accepts an untrusted query proposal and an explicitly
supplied SQLite path. Before opening a connection it requires one bounded,
parameterized `SELECT` (or non-recursive `WITH ... SELECT`) over only
`saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`; rejects unsafe
syntax, operations, tables, parameters, joins, and unbounded results; and never
interpolates values into SQL.

Execution opens a fresh SQLite URI connection with `mode=ro`, enables
`query_only`, disables trusted-schema behavior, installs a deny-by-default
authorizer and progress handler, and uses `Connection.execute` with bound
parameters. Row count, text-cell size, serialized result size, and JSON-safe
scalar output are bounded. Sanitized internal errors disclose no query,
database path, or SQLite details. Focused tests use temporary databases only
and verify that valid multi-night retrieval and adversarial attempts leave all
stored rows unchanged.

### Assignment 2 Part 2 hotel-advisor backend endpoint

```text
POST /api/hotel-advisor
{"question":"Which saved hotel has rooms from October 10 through October 12, and what is the total cost?"}
```

The route trims a required string question, limits it to 500 characters, and
returns HTTP 400 before any workflow stage for invalid input. For valid input it
calls the SQL proposer, passes the exact proposal and application database path
to the read-only executor, and passes the normalized question, accepted SQL,
bound parameters, and exact bounded records to the grounded-answer call. The
response contains `status`, `question`, `proposed_sql`, `query_parameters`,
`retrieved_records`, and `answer` for grading evidence.

Rejected or excessive queries return 422 without a second provider request;
database execution/result failures return 500. Missing provider configuration
returns 503, rate limits return 429, and authentication, model, transport,
provider, or malformed-response failures return a sanitized 502. A valid empty
retrieval still reaches the grounded-answer stage so it can explain the
no-match state. Focused route tests inject all three stages and use only the
temporary test database. A bounded October 8, 2026 browser smoke test also
verified the complete Vue/FastAPI/validator/read-only SQLite/persistence path
with deterministic local-only provider mocks. Live provider connectivity is
verified, while a correct grounded matching answer remains pending.

The prioritized OpenAI path now shares provider-neutral `QueryProposal`,
`GroundedAnswer`, and sanitized provider-error contracts with that existing
workflow. The repository-owned instructions are loaded explicitly from
`prompts/hotel-assistant.md`; the SHA-256 of its exact bytes is exposed
internally as the prompt version for later persistence.

The focused OpenAI client uses direct `httpx` requests to the Responses API,
`OPEN_AI`, and `OPENAI_MODEL`. It sends `store: false`, finite timeouts,
bounded output limits, and one forced strict function call for each stage. The
first result is converted to the shared untrusted query proposal; the second is
converted to the shared grounded answer and checked against record presence.
All OpenAI tests use `httpx.MockTransport`. The preserved OpenRouter client
continues to pass its compatibility tests, while `POST /api/hotel-advisor` now
uses the OpenAI proposal and grounded-answer callables by default. Mocked
end-to-end route tests exercise both model stages around real read-only
retrieval from a temporary database. A controlled live request later completed
both provider stages and the local read-only retrieval boundary. It produced a
grounded no-match result because the model bound the yearless October dates to
2024 instead of the stored 2026 demonstration dates. Focused prompt regression
coverage now requires the 2026 yearless-date rule. The subsequent live run used
2026 and retrieved records, but its checkout boundary and total were incorrect,
so a correct grounded live answer remains unverified.

Advisor history is now stored additively in `advisor_conversations`,
`advisor_messages`, and `advisor_runs`. A request without `conversation_id`
starts a conversation; a request with a known ID continues it with at most the
12 most recent user/assistant messages supplied as provider context. Short
transactions persist the user message and pending run before the first model
stage, the proposal and retrieval evidence between stages, and the assistant
message after success. Provider waits never hold a SQLite write transaction.
Failed attempts retain only a safe category and message.

Successful advisor responses preserve the grading fields and additionally
return `conversation_id`, `user_message_id`, `assistant_message_id`, `run_id`,
and `prompt_version`. The read-only history endpoints are:

```text
GET /api/advisor/conversations
GET /api/advisor/conversations/{conversation_id}
```

They return bounded user-visible conversation information only. They do not
return hidden prompts, audit SQL, provider metadata, credentials, raw errors,
or database paths. Persistence and follow-up behavior have been verified with
temporary SQLite databases and mocked provider responses in both automated and
visible-browser checks, including page refresh and full service restart. One
live OpenAI no-match workflow and the later incorrect-answer workflow both have
refresh/restart persistence evidence; a correct matching answer remains
pending.

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
search. It now checks SQLite first. Saved matches are labeled **Saved locally**,
include the five dated simulated rate/room rows, and are explicitly described as
an incomplete subset. Only a successful empty local lookup falls through to the
existing live endpoint, whose results are labeled **API results**. A local
database error stops the search instead of contacting Geoapify. Live result
cards offer **Add to Local**; saved provider IDs are reloaded after page refresh,
and saved cards offer **Remove from Local**. The list and markers continue to
share one selected provider place ID. Leaflet uses standard OpenStreetMap tiles
with visible tile attribution, and provider identity/location attribution stays
visible for live and saved records. Automated checks and the bounded October 1,
2026 browser verification passed. That verification covered frontend Add and
Remove, refresh and full-service restart persistence, local-first Network
behavior, DB Browser editing, the visible edited rate/room values, existing
workflow regressions, and a clean console.
Search for a hotel,
choose a traveler and one of the displayed offered stays, and use **Create
booking**. The booking-history table is loaded from SQLite and provides
**Cancel**, **Delete**, and **Refresh history** actions. Cancelled records remain
visible; deleted records disappear only after the backend confirms deletion and
history is reloaded.

The **Ask about saved hotels** panel uses only the local FastAPI advisor routes.
It loads persisted conversation summaries at startup, reopens the most recently
updated conversation, supports new conversations and follow-up questions, and
reloads history from SQLite after a successful answer. It displays ordered
messages, proposed SQL, bound parameters, retrieved local records, the grounded
answer, and answered/no-match/insufficient-data status. Nightly rates and room
availability are labeled as simulated course data. Advisor errors remain
isolated from ZIP, nearby-hotel, map, Assignment 1 search, and booking state.
API-client tests, both linters, and the production build pass. The bounded
mocked browser check verified loading and disabled controls, ordered new and
follow-up messages, grading evidence, new/reopened conversations, refresh and
restart persistence, safe failures, isolated existing travel state, and a
clean console. No external provider request was made during that mocked check.
A later controlled live workflow completed both OpenAI stages, validated and
executed one read-only query, and persisted its grounded no-match result. The
model chose 2024 for the yearless October question rather than the stored 2026
dates. The prompt correction caused the next live proposal to use 2026, but it
bound checkout to October 13 and the answer reported $32.55 for records totaling
$325.50. Both runs remain connectivity, persistence, and boundary evidence—not
final matching-answer submission evidence.

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

## Assignment 2 Part 2 chatbot checkpoint

The reviewed chatbot implementation and accepted evidence are preserved in
[`acdd832c1a78c0351238ca18f1c54bb6b90340b7`](https://github.com/NateHudson214/hudson-travel/commit/acdd832c1a78c0351238ca18f1c54bb6b90340b7).
The non-fast-forward merge into `main` is
[`6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef`](https://github.com/NateHudson214/hudson-travel/commit/6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef).
The student completed the final VS Code review, and the complete automated,
documentation, evidence, protected-file, ignore, and read-only database gate
passed on the feature branch and merged `main`. The feature branch and final
merged checkpoint are published; Canvas submission remains a manual step.
