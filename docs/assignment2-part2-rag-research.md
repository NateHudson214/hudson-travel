# Assignment 2 Part 2 — RAG Chatbot Research and Early Design

**Observation date:** October 8, 2026
**Stage:** Research, backend persistence, and the Vue advisor are implemented.
The mocked visible-browser, refresh, and restart workflow is verified. One live
OpenAI two-stage no-match workflow is also verified. The focused 2026
yearless-date prompt correction and regression coverage are complete. A second
live run selected 2026 and retrieved matching records, but exposed separate
checkout-boundary and answer-arithmetic defects, so final matching evidence is
still pending.

On October 8, 2026, the initial controlled live request failed authentication
because the ignored `.env` value contained an extra variable-name fragment.
After the student replaced it with a new Default-project key, a sanitized
first-stage diagnostic returned HTTP 200. One subsequent Vue request completed
both live `gpt-6-luna` stages. The generated query passed the local validator,
but bound the yearless dates to October 10–12, 2024 rather than the stored 2026
demo dates. Retrieval was therefore empty and the grounded response correctly
reported no match. This proves provider connectivity and the complete boundary,
but not the intended matching-answer example. The repository prompt now records
the October 10–14, 2026 course-data range and requires yearless October ranges
to use 2026 without overriding an explicit year.

The one authorized corrected-year rerun on October 8 used `2026-10-10` through
`2026-10-13`, retrieved three rows totaling 32550 cents, and returned `$32.55`.
The year rule therefore worked, but the proposed checkout did not match the
required `2026-10-12` boundary and the answer was not grounded arithmetically.
No retry occurred, and the result was not retained as success evidence.

The smallest robust correction does not parse free-form currency. The internal
grounded-answer tool now carries `total_cost_cents` and requires the model to
place a fixed `{{total_cost}}` marker in its prose. At the provider-neutral route
boundary, the integer must exactly match a retrieved `total_cost_cents` value;
the backend then formats cents as dollars. The public endpoint contract stays
unchanged. The prompt separately fixes the required range as October 10
inclusive through the October 12 checkout boundary, excluding October 12.
Mocked tests cover correct `$200.00` rendering and decimal-shift rejection; no
new live call had occurred at that stage. The next authorized live attempt
stopped after its proposal was rejected by the local SQL safety boundary. The
second provider stage did not run, and no retry or success evidence followed.

The persisted rejection was then diagnosed locally without executing the SQL.
The proposal used `UNION` and three joins, so it violated two deliberate
validator limits rather than exposing a validator compatibility gap. The
validator remains unchanged. The prompt now narrows the required demonstration
shape to one flat `SELECT`, exactly two joins across the approved tables, the
fixed inclusive/exclusive date predicates, grouped availability checks, and an
integer-cent total. Mocked integration verifies this shape only; corrected live
evidence was still pending at that stage.

The final authorized live run on October 9, 2026 confirmed the narrowed prompt
shape. The first stage returned one flat, two-join proposal with the exact 2026
date boundary; the validator accepted it and read-only retrieval returned the
two stored nights and 20000-cent total. The second stage returned the exact
structured total and marker, allowing the backend to render `$200.00`. This is
the successful matching workflow; manual PNG/Network evidence capture remains
pending.

## Authoritative scope

Part 2 adds one grounded hotel-advisor workflow to the frozen Part 1 and
local-storage application:

1. A user asks a natural-language question about locally saved hotels and their
   clearly labeled simulated nightly data.
2. An LLM receives only the relevant schema and query rules and proposes one
   parameterized, read-only SQLite query.
3. The backend validates the proposal, executes it against the local database
   through a read-only connection, and collects a bounded result set.
4. A second LLM request receives the original question, accepted query, query
   parameters, and retrieved records.
5. Vue displays the question, proposed SQL, records, and a grounded actionable
   answer, or a clear no-match, insufficient-data, rejected-query, or provider
   failure state.

OpenRouter/Nemotron was the initial provisional provider and its mocked client
is preserved. The prioritized in-class provider is now OpenAI using
`gpt-6-luna` through the Responses API. Provider availability, pricing, and
rate limits are external conditions, not application guarantees. SQLite
retrieval is sufficient; no vector database is needed.

## Official sources

All sources below were inspected on October 6, 2026.

### OpenAI Responses API and model behavior

- GPT-6 Luna model reference:
  <https://developers.openai.com/api/docs/models/gpt-6-luna>
- Function-calling guide:
  <https://developers.openai.com/api/docs/guides/function-calling>
- Responses migration and storage guidance:
  <https://developers.openai.com/api/docs/guides/migrate-to-responses>

Provider-documented behavior and resulting decisions:

- `gpt-6-luna` supports the Responses API, function calling, strict structured
  outputs, and `reasoning.effort: none`.
- Responses function definitions place `name`, `description`, `parameters`, and
  `strict` directly on the function tool. Returned calls are separate `output`
  items with JSON-encoded `arguments`.
- Strict schemas require all properties and `additionalProperties: false`.
  Hudson Travel therefore represents arbitrary named SQL parameters as a
  strict array of required name/value objects, then converts that array to the
  shared dictionary contract before local validation.
- Responses are stored by default; Hudson Travel sends `store: false`.
- The client uses direct backend-only `httpx` calls, finite timeouts, bounded
  output, forced tools, and sanitized exceptions. Mock transports prove the
  contract without provider quota or a real key.
- `POST /api/hotel-advisor` now selects these OpenAI callables by default.
  Application state exposes a per-call HTTP transport provider so tests can
  exercise both provider stages and real temporary-database retrieval while
  guaranteeing that no live network request occurs.

### OpenRouter request, model, authentication, and service behavior

- Chat Completions API reference:
  <https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request>
- Tool calling guide:
  <https://openrouter.ai/docs/guides/features/tool-calling>
- Structured outputs guide:
  <https://openrouter.ai/docs/guides/features/structured-outputs>
- Quickstart and bearer authentication:
  <https://openrouter.ai/docs/quickstart>
- API-key reference:
  <https://openrouter.ai/docs/api/api-reference/api-keys/create-keys>
- Selected model page:
  <https://openrouter.ai/nvidia/nemotron-3.5-lightning%3Afree>
- Free-model collection:
  <https://openrouter.ai/collections/free-models/>
- NVIDIA models on OpenRouter:
  <https://openrouter.ai/nvidia>
- Current plan and free-tier information:
  <https://openrouter.ai/pricing/>

Provider-documented behavior:

- Non-streaming chat requests use
  `POST https://openrouter.ai/api/v1/chat/completions`, bearer authentication,
  and a JSON body containing `model` and `messages`.
- Tool definitions and `tool_choice` can constrain the model to return
  structured function arguments. The selected model page currently lists
  `tools` and `tool_choice` support, but not `response_format` support.
- The selected free model identifier is
  `nvidia/nemotron-3.5-lightning:free`. Its page advertised a 1,000,000-token
  context and showed approximately 93.55% three-day and 89.30% 24-hour
  availability when observed. Those percentages are a point-in-time status,
  not a promise.
- OpenRouter's pricing page listed 50 free requests per day when observed.
  Free models are subject to changing availability, provider routing, quota,
  and rate limits.
- The selected free endpoint warns that prompts may be logged for security and
  improvement and advises against sending confidential or personal data.
- API keys are sensitive bearer credentials and must remain in backend-only
  configuration. A newly created key is shown in plaintext only once.

Hudson Travel design decisions:

- Send only the user's course-project hotel question, the three-table schema,
  query rules, accepted SQL, bounded query parameters, and bounded retrieved
  records. Do not send user accounts, Assignment 1 booking history, secrets,
  environment variables, database paths, or unrelated tables.
- Use one forced tool named `propose_hotel_query` for the first call, with
  `parallel_tool_calls: false`. Its arguments contain only `sql` and
  `parameters`. Validate the returned JSON locally; tool support is not a
  security boundary.
- Use a low temperature, finite connect/read timeouts, and bounded output
  tokens. Do not rely on unavailable `response_format` support.
- Make a second ordinary chat request only after the query passes validation
  and executes successfully. Instruct it to use only the supplied records,
  disclose simulated rates/availability, identify missing information, and
  avoid inventing hotels, dates, prices, rooms, or booking capability.
- Map authentication, quota/rate-limit, timeout, provider HTTP, malformed
  response, and unavailable-model failures to safe backend errors. Never return
  the key, request headers, complete provider URL, or raw exception text.

### SQLite read-only execution and safeguards

- SQLite URI filenames and `mode=ro`: <https://www.sqlite.org/uri.html>
- SQLite PRAGMA reference (`query_only`, `trusted_schema`):
  <https://www.sqlite.org/pragma.html>
- SQLite authorizer callback: <https://www.sqlite.org/c3ref/set_authorizer.html>
- Python `sqlite3` reference:
  <https://docs.python.org/3/library/sqlite3.html>

SQLite- and Python-documented behavior:

- A URI connection opened with `mode=ro` rejects database writes at the
  connection layer.
- `PRAGMA query_only = ON` independently prevents data-changing statements on
  that connection. `PRAGMA trusted_schema = OFF` reduces the risk from schema
  content invoking unsafe application-defined behavior.
- `Connection.set_authorizer()` can return `SQLITE_DENY` for prohibited SQL
  operations and table/column access.
- `Connection.set_progress_handler()` can interrupt a query after a bounded
  amount of virtual-machine work.
- `Connection.execute()` accepts one statement; `executescript()` is not
  appropriate for untrusted proposals. Parameter placeholders bind values
  without directly interpolating user or model text.
- `sqlite3.complete_statement()` only detects syntactic statement termination;
  it is not a security parser or validator.

Hudson Travel defense-in-depth decisions:

1. Reject a missing/blank question and cap the trimmed question at 500
   characters before any provider call.
2. Require exactly one `propose_hotel_query` tool call. Parse strict JSON, allow
   only `sql` plus a parameter object, cap the SQL at 4,000 characters, and cap
   parameter count and scalar lengths.
3. Never place the question or parameter values into SQL text. Require named
   placeholders and bind a backend-validated dictionary. Dates remain ISO
   strings; rates remain integer cents.
4. Reject comments, semicolons, multiple statements, `PRAGMA`, `ATTACH`,
   `DETACH`, transaction commands, DDL, DML, extension loading, and references
   to temporary or SQLite-internal schemas before preparing the statement.
   Accept only a single `SELECT` or non-recursive `WITH ... SELECT` proposal.
5. Open a new SQLite URI connection with `mode=ro`, set
   `PRAGMA query_only = ON` and `PRAGMA trusted_schema = OFF`, and never enable
   extension loading.
6. Install an authorizer that allows only read operations on
   `saved_hotels`, `saved_hotel_searches`, and `demo_hotel_nights`, plus the
   minimal `SELECT` and allowlisted aggregate/scalar functions needed for the
   task. Deny every write, schema change, PRAGMA, attach/detach, transaction,
   virtual-table, and unknown-function action.
7. Limit the query shape to the three allowed tables, each at most once, with
   no recursive CTE, compound query, or more than two joins. Require a bounded
   result; the backend also fetches at most 51 rows and rejects a result beyond
   the 50-row response cap.
8. Use a progress handler to abort excessive virtual-machine work and apply
   response cell/string-size limits before any records are sent to the second
   LLM request.
9. Execute only with `Connection.execute(sql, parameters)`. Do not use
   `executescript`, dynamically registered SQL functions, or model-provided
   identifiers outside the allowlist.
10. Return sanitized validation and provider errors. Do not reveal credentials,
    raw provider payloads, full provider URLs, database paths, or internal SQL
    errors to Vue.

Lexical rejection is only an early filter. The read-only URI, query-only mode,
authorizer, bounded execution, parameter binding, and table/column allowlists
remain authoritative even if a proposal bypasses a string check.

## Relevant local schema

Only these existing additive Assignment 2 tables are exposed to the LLM. The
Assignment 1 hotels, trips, users, and bookings tables remain out of scope.

### `saved_hotels`

| Column | Meaning |
| --- | --- |
| `hotel_id` | Geoapify provider place ID and primary key |
| `name` | Optional provider hotel name |
| `address` | Optional provider formatted address |
| `latitude` | Provider latitude |
| `longitude` | Provider longitude |

### `saved_hotel_searches`

| Column | Meaning |
| --- | --- |
| `hotel_id` | Saved hotel foreign key |
| `zip_code` | Searched five-digit ZIP; part of the composite primary key |
| `postcode` | Resolved provider postcode |
| `country_code` | Resolved country code |
| `latitude` | Resolved search-center latitude |
| `longitude` | Resolved search-center longitude |
| `locality` | Optional resolved locality |

### `demo_hotel_nights`

| Column | Meaning |
| --- | --- |
| `hotel_id` | Saved hotel foreign key; part of the composite primary key |
| `stay_date` | Simulated night in ISO `YYYY-MM-DD` form; remaining primary key |
| `nightly_rate_cents` | Nonnegative simulated nightly rate in integer cents |
| `rooms_available` | Nonnegative simulated room count |

For a stay from October 10 through October 12, the requested nights are October
10 and 11; checkout October 12 is excluded. A hotel is available only when
every requested night exists and has `rooms_available > 0`. Total cost is the
sum of the requested nights' integer cents. A missing night produces an
insufficient-data/not-available conclusion, never an assumed rate or room.

## Provisional backend contract

The smallest contract remains one endpoint:

```text
POST /api/hotel-advisor
Content-Type: application/json
```

Request:

```json
{
  "question": "Which saved hotel has rooms from October 10 through October 12, and what is the total cost?",
  "conversation_id": null
}
```

Successful or honestly empty response:

```json
{
  "status": "answered",
  "question": "Which saved hotel has rooms from October 10 through October 12, and what is the total cost?",
  "proposed_sql": "SELECT ... WHERE stay_date >= :check_in AND stay_date < :check_out ...",
  "query_parameters": {
    "check_in": "2026-10-10",
    "check_out": "2026-10-12"
  },
  "retrieved_records": [],
  "answer": "...",
  "conversation_id": "C000001",
  "user_message_id": "M000001",
  "assistant_message_id": "M000002",
  "run_id": "R000001",
  "prompt_version": "sha256:..."
}
```

`status` is one of `answered`, `no_matches`, or `insufficient_data`. These
states can remain HTTP 200 because the request completed safely. Blank or
oversized questions map to HTTP 400. A rejected model proposal and provider or
malformed-response failures use safe error responses and do not execute SQL or
make the second provider call. Tests lock the safe 400, 404, 422, 429, 500,
502, and 503 mappings for their documented cases.

Keeping `query_parameters` in the response is a small addition to the suggested
grading fields: it makes the displayed SQL understandable without replacing
placeholders with unsafe string interpolation. The response exposes no hidden
prompt, credential, provider metadata, or database path.

The persistence design is now implemented with additive conversations,
ordered user/assistant messages, and execution runs. Runs retain the versioned
prompt identifier, proposal, accepted/executed SQL, parameters, bounded records,
completion state, and safe failures. Independent transactionally advanced
counters prevent ID reuse. Provider calls occur between short transactions,
never inside them. A follow-up supplies at most the 12 latest persisted visible
messages; hidden instructions and audit fields are not conversation content.
The public history endpoints expose only bounded summaries and messages.
`docs/rag-context.md` records the precise data and security boundary.

The implemented Vue panel follows the early mockup's evidence-first hierarchy:
persisted conversation messages remain primary, followed by the grounded
answer, proposed SQL, parameters, and retrieved records. It reopens backend
history on load and keeps advisor failures isolated from every existing travel
workflow. An October 8, 2026 bounded browser check confirmed these decisions,
including refresh and full-service restart persistence, using deterministic
local-only provider mocks and a temporary database. This is not evidence of a
live OpenAI request. The later controlled live no-match and corrected-year
results are recorded above; correct matching-result verification remains
pending.

## Two-call workflow

```text
Vue question
  -> POST /api/hotel-advisor
  -> first backend provider call: question + exact schema + query rules
  -> forced propose_hotel_query tool arguments
  -> local parser and layered SQL validator
  -> read-only bounded SQLite execution
  -> second backend provider call: original question + accepted SQL/params + rows
  -> grounded answer validation/sanitization
  -> Vue displays question, SQL, records, answer, and status
```

The backend owns both provider calls, validation, and retrieval. Vue never
contacts OpenAI or OpenRouter and never receives a key. The second prompt explicitly
states that the records are the only factual source and that nightly values are
simulated demonstration data.

## Test strategy

- Mock both provider calls. Automated tests must never consume provider quota
  or require a real key.
- Prove the first request contains only the relevant schema/rules and uses the
  exact model, forced tool, finite timeout, and no secret in surfaced errors.
- Accept a labeled valid parameterized query and verify the second request
  receives the original question, accepted query/parameters, and exact bounded
  records.
- Verify multiple-night inclusive-check-in/exclusive-checkout totals, rooms on
  every requested night, missing-night insufficiency, no matches, nullable hotel
  fields, and integer-cent formatting responsibility.
- Reject proposals containing multiple statements, comments, semicolons,
  writes, DDL, `PRAGMA`, `ATTACH`, transactions, recursive CTEs, compounds,
  unknown tables/columns/functions, excessive joins, missing placeholders,
  oversized parameters, or unbounded/excessive results.
- Prove the authorizer denies disguised writes and unrelated Assignment 1
  tables even when earlier text checks miss them.
- Prove the progress limit interrupts excessive work and that validation failure
  prevents both database execution and the second provider call.
- Snapshot relevant row counts and content before and after adversarial tests to
  prove the ignored development database is never used or mutated; tests use
  temporary SQLite files.
- Cover missing configuration, authentication/rate-limit/HTTP/timeout/network
  failure, unavailable model, malformed tool arguments, and malformed final
  answers with safe messages containing no key or raw provider details.
- Preserve and rerun the complete existing backend and frontend suites so Part
  1 search, map, local-first storage, Add/Remove, persistence, Assignment 1
  behavior, and attribution remain frozen.

## Dependency finding

The backend already directly declares and imports `httpx`, which supports the
required authenticated JSON POST requests and finite timeouts. The existing
`python-dotenv` configuration capability and Python standard-library `sqlite3`
are also sufficient. No OpenRouter SDK, SQL parser, vector database, or other
new dependency is currently justified. This finding will be reconfirmed in a
separate capability/configuration check before implementation.

## Early mockup

The repository-native early design is
[`docs/mockups/assignment2-part2-rag-early.svg`](mockups/assignment2-part2-rag-early.svg).
It is intentionally labeled **early design — not implemented** and includes the
question, loading, SQL, retrieved-record, grounded-answer, no-match,
insufficient-data, unsafe-query rejection, provider-failure, and simulated-data
states required for implementation and verification planning.
