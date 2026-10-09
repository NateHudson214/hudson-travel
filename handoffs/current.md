# Current Handoff

**Updated:** October 8, 2026

**Checkpoint:** Assignment 1, Assignment 2 Part 1, and the additive local-hotel
storage workflow remain preserved and published. Assignment 2 Part 2 work is on
`assignment2-part2-rag-chatbot`. Research, backend-only configuration,
provider-neutral contracts, preserved mocked OpenRouter support, the mocked
OpenAI Responses client, read-only retrieval, and the mocked
`POST /api/hotel-advisor` orchestration route, durable history, and the Vue
advisor interface are implemented. The bounded mocked browser, refresh, and
service-restart verification passed October 8, 2026. A later controlled live
workflow completed both OpenAI stages, read-only retrieval, and durable
refresh/restart restoration. Its yearless October question was bound to 2024,
so it produced a truthful no-match rather than the intended matching 2026
answer. The versioned prompt and focused regression tests now enforce 2026 for
yearless October ranges. One authorized rerun used 2026 and persisted normally,
but chose checkout October 13 and reported $32.55 for records totaling $325.50.
No retry, dependency change, unrelated mutation, or success screenshot occurred.
The subsequent mocked-only correction fixes the required checkout boundary and
adds deterministic backend cents formatting without changing the public route.
The next one-shot live attempt persisted `C000004`, `M000008`, and failed run
`R000006`; the proposal was rejected locally as `unsafe_query`, so no assistant
message, retrieval, grounded-answer request, retry, or success evidence exists.
The read-only diagnosis found `UNION` and three joins, confirming that the
validator behaved correctly. The prompt-only correction requires one flat
`SELECT` and exactly two joins for the demonstration; mocked coverage was the
only verification immediately after that change, so a corrected live result
was still pending at that point.
The final authorized October 9 live run then passed: the accepted flat query
used exactly two joins and the exact date boundary, retrieval returned two
nights and 20000 cents for Hotel State College, and the grounded answer displayed
`$200.00`. `C000005`, `M000009`, `M000010`, and `R000007` persisted through
refresh and restart without another provider request. A focused read-only
history extension now restores the completed SQL, parameters, records, answer,
run ID, and prompt version when `C000005` is reopened. Automated and visible
restart verification passed with GET requests only and a clean console. Manual
PNG capture was reviewed and accepted by the student. The Network image records
GET-only restoration; the advisor image shows the question, answer, and
simulated-data disclosure, while its lower fields are supported by the recorded
browser verification. The retained services were stopped and both ports were
confirmed free.

## Assignment 2 Part 2 RAG research stage

- The authoritative endpoint is a two-request grounded workflow: the LLM first
  proposes SQL using a narrow schema and rules; the backend validates and runs a
  read-only local query; the original question and bounded retrieved records
  then return to the LLM for a grounded answer.
- OpenAI is now the prioritized provider using `gpt-6-luna`; the earlier
  OpenRouter/Nemotron client remains preserved. Provider availability, pricing,
  quotas, and routing are external and may change.
- The schema exposed to this feature is limited to `saved_hotels`,
  `saved_hotel_searches`, and `demo_hotel_nights`. Assignment 1 records and
  unrelated tables are excluded.
- The implemented mocked API is `POST /api/hotel-advisor` with a `question` and
  optional `conversation_id`. Its grading response preserves status, question,
  proposed SQL, bound parameters, retrieved records, and answer, and adds the
  conversation, message, run, and prompt-version identifiers.
- The intended SQL boundary combines a single parameterized SELECT, explicit
  table/column/function allowlists, SQLite URI `mode=ro`, `query_only`,
  `trusted_schema=OFF`, an authorizer callback, progress and row limits, and
  safe errors. A model-proposed query is never trusted merely because it came
  from a forced tool call.
- Existing `httpx`, `python-dotenv`, and standard-library `sqlite3` capabilities
  appear sufficient. No dependency was installed or changed during research.
- Research and security/test decisions are in
  `docs/assignment2-part2-rag-research.md`.
- Shared contracts and sanitized failure categories are provider-neutral. The
  OpenAI client loads `prompts/hotel-assistant.md` through an explicit path and
  exposes a deterministic SHA-256 prompt version for later persistence.
- Mocked OpenAI tests cover the exact Responses endpoint and payload, strict
  function schemas, proposal/answer parsing, all three result statuses, and
  safe configuration/auth/rate/model/HTTP/transport/response failures. Those
  tests make no live request; the later live no-match run is recorded below.
  The route now uses the OpenAI callables by default; OpenRouter remains
  preserved as compatibility work.
- A per-call application-state transport provider lets end-to-end tests make
  both OpenAI stages use fresh `MockTransport` instances. The tests execute an
  accepted proposal through the real read-only query layer against a temporary
  database, pass the exact records to the second call, and verify answered,
  no-match, insufficient-data, blocked-write, and provider-failure behavior.
- The early, explicitly unimplemented interface is
  `docs/mockups/assignment2-part2-rag-early.svg`.
- The ignored development database remains intact with one saved hotel, one ZIP
  association, and five demo nights; the reviewed October 12 values remain
  12550 cents and 7 rooms.
- The route validates a trimmed 500-character question before any stage, then
  runs injectable proposal, read-only retrieval, and grounded-answer callables
  in order. Its second forced tool result contains only status and answer, and
  local checks enforce record/status consistency.
- Focused mocked tests cover all three statuses, exact stage inputs, early-stop
  behavior, safe 400/422/429/500/502/503 mappings, and credential/path/query
  sanitization. No live provider request is part of this stage.
- Additive `advisor_conversations`, `advisor_messages`, and `advisor_runs`
  persist ordered visible history plus proposed/executed query evidence,
  bounded retrieval data, prompt version, status, and safe failures. Durable
  counters allocate non-reused `C`, `M`, and `R` IDs in short transactions.
- Follow-ups send at most 12 ordered prior user/assistant messages to both
  mocked OpenAI stages. History endpoints expose only bounded visible content.
  Temporary-database tests cover reinitialization, failed attempts, unknown
  conversations, and safe field exclusion.
- `HotelAdvisor.vue` and `frontend/src/api/advisor.js` now load and reopen
  conversations, start new threads, send follow-ups, reread SQLite-backed
  messages, and render SQL, parameters, records, answer, and status. Failures
  retain valid history and clear stale evidence without touching travel state.
- The frontend client suite, non-fixing linters, and 28-module production build
  pass. No component-test capability was added.
- The bounded mocked browser workflow passed with zero source-correction
  cycles. It exercised grounded new and follow-up questions, SQL/parameter/row
  evidence, new/reopened history, refresh and restart persistence, no-match and
  insufficient-data states, and safe 404/422/429/500/502/503 outcomes.
- The final temporary state had `C000001` through `C000003`, `M000001` through
  `M000019`, and `R000001` through `R000012`, with next counters 4, 20, and 13,
  no foreign-key violations, and no duplicate rows. The temporary services and
  database were removed after verification; the ignored development database
  stayed unchanged.
- Existing entered-ZIP, saved/local-first hotel/map and attribution, Harbor
  Lantern T001/T009, and booking-history behavior passed without mutation; the
  healthy console had no warnings or errors.
- The initial controlled live attempts returned local HTTP 502 because the
  ignored `OPEN_AI` value was malformed. A sanitized diagnostic identified
  HTTP 401 `invalid_api_key`; the student replaced the key without exposing it.
- The authorized live Vue run then completed as `C000002`, messages `M000004`
  and `M000005`, and `R000004`, with the current prompt version. Its accepted
  query used only the three approved tables, but parameters selected 2024-10-10
  through 2024-10-12. Retrieval was empty and the grounded status was
  `no_matches`. Refresh and full restart restored it without another POST.
- The browser console remained clean. Backend logs showed exactly one local
  `POST /api/hotel-advisor`; no credential appeared in the UI. All pre-existing
  travel-table hashes remained unchanged and foreign-key integrity passed.
- The focused correction adds the October 10–14, 2026 course-data range and
  requires 2026 for yearless October month/day ranges while preserving an
  explicit user year. Prompt, client, route-integration, validator, and
  persistence regression tests pass without live traffic.
- The corrected-year live run persisted as `C000003`, messages `M000006` and
  `M000007`, and `R000005`, using prompt version
  `sha256:929d2aa1fa49742461662563e2067ea7bb4c23266f51097aa574575f48356173`.
  Refresh and full service restart restored it without another advisor POST;
  the browser console was clean.
- The follow-up mocked regression coverage requires `2026-10-10` through the
  excluded `2026-10-12` checkout, retrieves two 10000-cent nights, and renders
  `$200.00` from a verified structured integer. Shifted totals and free-form
  provider dollar amounts are rejected before assistant-message persistence.
- The persisted `R000006` proposal was inspected read-only and never executed.
  It contained a prohibited compound `UNION` and three joins, so no validator
  compatibility change was justified.
- The prompt now requires one flat non-compound demonstration query with exactly
  two joins, the 2026-10-10/2026-10-12 boundary, grouped availability checks,
  and integer-cent totals. Mocked tests verify the safe shape and `$200.00`
  grounding; no live provider request followed this correction.
- The final separately authorized two-call demonstration passed as `C000005` /
  `R000007`. Refresh and restart used only history GET requests, and the browser
  console remained clean.
- The optional `latest_completed_run` history field now restores only safe
  completed evidence. Failed and pending runs do not appear as successful
  evidence, and no executed SQL, provider detail, hidden prompt, error, or
  database path is exposed.
- The reviewed Network evidence shows only the local conversation-list and
  `C000005` GETs. The student accepted the readable advisor screenshot as
  supporting evidence; fields below its crop remain verified separately.
- Next step: manually capture and review the successful advisor and browser
  Network evidence files, then update the documentation and stop the retained
  services. Do not submit another advisor question.

## Assignment 2 Part 2 current stage

- The student manually verified the empty additive `saved_hotels` and
  `demo_hotel_nights` schema in DB Browser without writing changes.
- `saved_hotel_searches` now stores a unique provider-hotel/searched-ZIP pair
  plus the resolved location context. Initialization is additive and repeatable.
- Saving one provider hotel, its ZIP association, and the five October 10–14,
  2026 demo nights is one transaction. Repeated saves preserve edited rate and
  room values.
- Removing a provider hotel transactionally cascades only its saved associations
  and demo nights. Assignment 1 tables remain separate.
- The API exposes saved IDs, saved hotels by validated ZIP, create, and delete.
  Valid empty local searches return HTTP 200; database failures return a safe
  error rather than falling through to Geoapify.
- Vue loads saved IDs after refresh and performs a local ZIP lookup before live
  search. Saved matches are labeled **Saved locally** and show simulated dated
  data; live fallback results are labeled **API results**.
- Add and Remove controls wait for backend confirmation. Existing list/map
  synchronization and keyboard selection use the same provider IDs for both
  result sources.
- Automated verification passed with 123 backend tests, 29 frontend client
  tests, both linters, and a 26-module build. The same two non-failing framework
  dependency warnings remain.
- The bounded October 1 browser run made one live `16802` request only after an
  empty local result, added two hotels, and proved saved-only local lookup after
  refresh without another provider request.
- The student changed Hotel State College's October 12 demo row to 12550 cents
  and 7 rooms in DB Browser. Vue displayed `$125.50` and 7, and the values
  survived a full backend/frontend restart.
- Scholar Hotel State College was removed through Vue with HTTP 204. After
  restart, SQLite retained exactly one hotel, one ZIP association, and five
  nights; the removed hotel remained absent and no rows duplicated.
- One correction cycle connected Leaflet marker keypress selection to the shared
  provider ID. The full gate and saved-result keyboard synchronization passed
  afterward.
- Existing ZIP controls, T001/T009 hotel search, eight booking rows,
  attribution, and the browser console all passed without booking mutation.
- The student captured and reviewed the edited-rate, local-first Network, and
  SQLite database screenshots. Visual inspection confirmed the required states,
  and the student confirmed that the files contain no key, secret, private, or
  unrelated material.
- Evidence paths: `evidence/assignment2-part2-edited-rate.png`,
  `evidence/assignment2-part2-local-first.png`, and
  `evidence/assignment2-part2-database.png`.
- Only the Hudson Travel services retained for evidence capture were stopped;
  ports 8000 and 5173 were confirmed free.
- The final manual VS Code review passed on October 5, 2026. The student
  confirmed that every visible change was intentional; all three evidence
  screenshots were correct and readable; secrets, generated dependencies,
  build output, caches, the ignored SQLite database, editor settings, and
  unrelated files were excluded; and all supplied CSV files and protected
  dependency declarations were unchanged.
- Implementation and evidence checkpoint:
  `77ae9b397caf3a3062d1ae8955aaf30cd0d1456d`
  (<https://github.com/NateHudson214/hudson-travel/commit/77ae9b397caf3a3062d1ae8955aaf30cd0d1456d>).
- Non-fast-forward merge checkpoint:
  `79e0b6ddd0acb1909059ef344d1bc369f78fe25e`
  (<https://github.com/NateHudson214/hudson-travel/commit/79e0b6ddd0acb1909059ef344d1bc369f78fe25e>).
- The full gate passed on the feature branch and merged `main`: 123 backend
  tests with the same two non-failing warnings, 29 frontend tests, both linters,
  the 26-module build, dependency and documentation consistency, protected and
  evidence hashes, and ignore checks. No live provider request was made.
- The feature branch and final `main` state are published. The next action is
  the student's required submission step; do not begin later work until asked.

## Assignment 2 Part 1 current stage

- The authoritative Part 1 scope is live hotel search and a synchronized map,
  not only the completed entered-ZIP demonstration.
- Research notes are in `docs/assignment2-part1-research.md`.
- The early, explicitly unimplemented design is
  `docs/mockups/assignment2-part1-early.svg`.
- The implemented backend flow resolves the exact U.S. ZIP, then requests up to 20
  `accommodation.hotel` features inside a strict 5,000-metre circle with
  proximity ordering.
- The implemented frontend uses one `selectedPlaceId` so list and map selection
  remain synchronized and keyboard-accessible.
- Hotel fields will remain provider-derived; missing values receive honest
  labels or omission, and no price, rating, availability, or booking claim will
  be invented.
- Geoapify and OpenStreetMap attribution must remain visible.
- `httpx` remains the declared backend HTTP client. Leaflet 1.9.4 is now an
  exact direct frontend dependency following the completed approval step.
- `GET /api/hotels/nearby?zip_code={zip_code}` returns the resolved location,
  5,000-metre radius, 20-result limit, and sanitized provider hotel records.
- Mocked controller and route tests cover request parameters, honest optional
  fields, invalid-feature exclusion, empty success, leading-zero ZIPs, safe
  errors, and coordinate handoff from geocoding to Places.
- Backend verification on September 28, 2026: 38 focused Places/route tests and
  95 complete backend tests passed. The complete suite retained the same two
  non-failing framework dependency warnings.
- Existing frontend verification remained green: 17 API-client tests, Oxlint,
  ESLint, and the 20-module Vite production build passed.
- `NearbyHotelSearch.vue` provides a separate validated ZIP flow with distinct
  initial, loading, validation, unresolved, empty, results, and service-error
  states while preserving both earlier ZIP lookup workflows.
- `NearbyHotelsMap.vue` owns one Leaflet map and replaceable marker layers. The
  parent owns `selectedPlaceId`, so list-button and marker selection stay on one
  provider identity.
- Provider names, addresses, and distances are rendered honestly; Geoapify and
  OpenStreetMap attribution are included, with no commercial travel fields.
- Frontend verification on September 29, 2026: all 23 API-client tests, Oxlint,
  ESLint, and the 25-module Vite production build passed.
- The bounded smoke test on September 29 used exactly one live nearby-hotel
  search for ZIP `16802`. It resolved State College and returned 20 provider
  hotels through the local FastAPI route.
- The live page showed 20 list results and 20 numbered map markers, a distinct
  search-center marker, and visible Geoapify, Leaflet, and OpenStreetMap
  attribution. List-to-marker and marker-to-list selection both passed.
- Local-only mocks verified loading, leading-zero ZIP `02113`, honest missing
  fields, empty results, 404 and 502 feedback, and stale-result clearing.
- All six invalid-input classes produced client validation without a backend
  request. Harbor Lantern Hotel still returned T001 and T009, eight existing
  booking-history records loaded, and no booking was changed.
- The healthy browser console had no warnings or errors. Zero correction cycles
  were required. Shortlist behavior remains unimplemented and outside Part 1.
- The student captured and reviewed all four required evidence files. The three
  PNGs are readable and visibly show the required live, synchronized-selection,
  and validation states. The readable QuickTime recording was manually reviewed
  by the student. No key, secret, private, or unrelated content was reported.
- The retained backend and frontend were stopped after capture; ports 8000 and
  5173 are free.
- The final VS Code review passed. The student confirmed that every visible
  change was intentional, evidence was correct, protected/generated/private
  files were excluded, CSV records were unchanged, and no shortlist or Part 2
  behavior was included.
- The implementation/evidence checkpoint is
  `0f38ae0ac35808e332ec91472bb0d5393e5adfc8` on the published
  `assignment2-part1-live-hotels` branch:
  <https://github.com/NateHudson214/hudson-travel/commit/0f38ae0ac35808e332ec91472bb0d5393e5adfc8>.
- The non-fast-forward merge checkpoint is
  `6739c4e5b4e4a93b74d6558253078024b1aa7cbf`:
  <https://github.com/NateHudson214/hudson-travel/commit/6739c4e5b4e4a93b74d6558253078024b1aa7cbf>.
- The complete automated gate passed on the feature branch and merged `main`.
  Both branches are published, Assignment 1 history remains intact, and the
  working tree is clean.

## Assignment 2 public API activity

- The backend-only Geoapify configuration helper and safe health status are in
  place; the credential is never returned to Vue.
- The fixed `GET /api/demo/zip-location` demonstration remains available and
  was observed resolving ZIP 16802 to State College on September 23, 2026.
- New `GET /api/zip-location?zip_code={zip_code}` accepts a string, trims it,
  and requires exactly five ASCII digits before calling the existing controller.
- The dynamic route preserves leading zeros and maps invalid input, unresolved
  ZIPs, missing configuration, and provider failures to safe 400, 404, 503, and
  502 responses.
- Vue now provides a labeled text input and dynamic lookup action. It validates
  five digits, disables both ZIP actions during a request, clears stale dynamic
  results on failure, and displays success in a plain location table.
- The fixed demonstration, hotel search, and booking interface remain intact.
- Geoapify hotel retrieval, the results list, and the Leaflet map extend the
  earlier ZIP-foundation activity and are now implemented and smoke-tested for
  Assignment 2 Part 1. Shortlist behavior and its new persistence remain
  outside Part 1.

## Assignment 2 automated verification

- Focused backend ZIP-route tests: 19 passed.
- Complete backend suite: 57 passed with the same two non-failing framework
  dependency warnings.
- Frontend API-client tests: 17 passed.
- Oxlint and ESLint: passed without auto-fix and without findings.
- Vite production build: passed; 20 modules transformed.
- No live Geoapify request was made during the implementation gate.
- Dynamic browser verification passed September 23, 2026; the two PNG files and
  student recording remain pending.

## Assignment 2 browser verification

- Live entered ZIP `16802` returned State College, country `us`, latitude
  `40.803167822`, and longitude `-77.861384958` through the local FastAPI path.
- Loading feedback appeared and both ZIP controls were disabled during a
  delayed local-only response.
- A local-only `02113` response retained its leading zero in the table.
- Blank, short, long, alphabetic, punctuation, and Unicode-digit input showed
  the five-digit validation message and no stale result table.
- Local-only unresolved and provider-failure responses showed safe 404 and 502
  feedback and cleared stale results.
- `Harbor Lantern Hotel` still returned T001 and T009.
- The healthy browser console contained no warnings or errors.
- Zero source correction cycles were needed.
- The first attempted automated field clear did not alter the actual value and
  unintentionally repeated the successful 16802 provider request once.
- After backend restoration, unexpected local requests for ZIPs 18042–18050
  appeared from browser activity outside the scripted smoke-test inputs. The
  backend was stopped immediately; the source of those requests was not proven.
- The successful screenshot-ready state was recreated with the exact observed
  live values through a one-request local mock. The mock is stopped. This
  recreated state must not be described as a second live verification.

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

Upload the updated `report.md` to the Assignment 2 Part 1 Canvas submission and
provide the repository URL, assessed implementation checkpoint, and reviewed
demonstration recording as requested. Do not add shortlist behavior, new
persistence, or begin Part 2 until the student explicitly starts that work.

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

## Assignment 2 Part 2 chatbot checkpoint

- Implementation/evidence commit:
  [`acdd832c1a78c0351238ca18f1c54bb6b90340b7`](https://github.com/NateHudson214/hudson-travel/commit/acdd832c1a78c0351238ca18f1c54bb6b90340b7).
- Non-fast-forward `main` merge:
  [`6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef`](https://github.com/NateHudson214/hudson-travel/commit/6ea8d491e286e11bdbc2dbb0c714d7a66a4ff7ef).
- The final VS Code review and complete feature/merged-main gates passed. The
  accepted evidence hashes and ignored database checksum remained unchanged.
- The feature branch and final merged checkpoint are published. The remaining
  action is the student's manual Canvas submission; no later work has begun.
