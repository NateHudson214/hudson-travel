# Hudson Travel RAG Context

**Status:** Implemented backend persistence and mocked-provider boundary as of
October 8, 2026. Mocked Vue/browser verification passed. A controlled live
OpenAI workflow completed both provider stages, read-only retrieval, and
refresh/restart persistence. The model interpreted the yearless October dates
as 2024, so it returned a grounded no-match instead of querying the stored 2026
demo nights. The prompt now requires 2026 for yearless October ranges while
preserving explicit user-provided years. A later live run used 2026 but chose
checkout October 13 and returned an incorrect decimal total, so the corrected
grounded demonstration remains pending.

The current mocked-only correction defines October 12 as the excluded checkout
boundary for the required question. A total-cost query returns integer
`total_cost_cents`; the model supplies the exact retrieved integer and a fixed
marker, while the backend performs the only cents-to-dollars formatting.
Unsupported totals and provider-written dollar amounts are rejected safely.
The latest live attempt did not reach this grounding safeguard because its SQL
proposal was rejected locally before retrieval; the answer stage was not made.
Read-only diagnosis showed that proposal used `UNION` and three joins. The
existing validator correctly blocks both shapes. The prompt now requires the
demonstration proposal to use one flat `SELECT` with exactly two joins; the
validator and database remain unchanged, and only mocked verification has run
since that correction.

The final controlled run on October 9, 2026 passed this boundary. Its flat
two-join proposal used only the approved tables and exact 2026 parameters.
Read-only retrieval returned two nights, 20 minimum rooms, and 20000 cents for
Hotel State College; the backend rendered the grounded `$200.00` answer. The
conversation persisted through refresh and service restart without another
provider request. The conversation-detail response now exposes only the latest
completed run's safe evidence fields, allowing Vue to restore the same SQL,
parameters, records, answer, IDs, and prompt version after another full service
restart without an advisor POST. Manual evidence capture remains outstanding.
The reviewed Network PNG records that GET-only restoration. The student also
reviewed and accepted the companion advisor PNG, which shows the saved question,
`$200.00` answer, and simulated-data disclosure. The lower SQL, parameters,
record, run ID, and prompt version were verified in the visible browser and
automated checks rather than being visible in that screenshot crop.

## Allowed local hotel data

The advisor may retrieve from exactly these SQLite tables:

- `saved_hotels`: provider hotel ID, optional provider name and address, and
  provider latitude/longitude.
- `saved_hotel_searches`: saved hotel ID, searched five-character ZIP,
  resolved postcode/country/coordinates, and optional locality.
- `demo_hotel_nights`: saved hotel ID, stay date, integer nightly rate in cents,
  and rooms available.

The model never connects to SQLite. It proposes one query; the backend validates
and executes that query locally through a read-only connection.

## Honest simulated-data rules

- Nightly rates and rooms are simulated course data, not provider inventory.
- The simulated course-data date range is October 10–14, 2026. A yearless
  October month/day range binds to 2026; an explicit user-provided year is
  preserved, and no other year may be invented or substituted.
- A stay uses each night from check-in inclusive through checkout exclusive.
- Availability requires every requested night to exist with rooms greater than
  zero. Missing nights are insufficient data and cannot be assumed available.
- Total cost is the sum of stored integer cents for the requested nights.
- Missing hotel names, addresses, nights, rates, or availability stay missing.
  The answer must not invent prices, rooms, ratings, amenities, or booking claims.

## Read-only query boundary

Only one bounded parameterized `SELECT`, or a non-recursive `WITH ... SELECT`,
is accepted by the general static validator. The narrower model prompt requires
one flat `SELECT` for the graded demonstration. The validator restricts tables,
columns, functions, parameters,
joins, and output size. It rejects comments, multiple statements, unbounded
output, writes, schema changes, `PRAGMA`, `ATTACH`, transactions, dangerous
functions, recursive queries, and unrelated Assignment 1 tables.

Execution uses a SQLite URI opened with `mode=ro`, `PRAGMA query_only = ON`,
`PRAGMA trusted_schema = OFF`, a deny-by-default authorizer, bound parameters,
a progress limit, and bounded JSON-safe results.

## Conversation-history boundary

`advisor_conversations` identifies a durable thread. `advisor_messages` stores
ordered user and assistant content only. A follow-up sends at most the 12 most
recent stored messages, in order, plus the new question. The versioned system
prompt is loaded separately and is never persisted as user-visible content or
returned by a history endpoint.

`advisor_runs` stores the prompt version, normalized question, proposed SQL,
accepted/executed SQL, bound parameters, bounded retrieved records, completion
status, timestamps, and a sanitized error category/message when a stage fails.
It provides local grading and debugging evidence without becoming model-visible
conversation content.

## Excluded information

No advisor table, history response, or surfaced error may contain:

- API keys or key fragments
- authorization headers
- provider request URLs or raw provider responses
- hidden/system prompt text
- raw exceptions or database paths
- unrelated Assignment 1 records

Automated verification uses temporary SQLite files and mocked provider traffic.
The ignored development database is not part of this implementation check.
