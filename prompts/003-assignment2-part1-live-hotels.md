# Assignment 2 Part 1 — AI Prompt Evidence

**Tool and model:** OpenAI Codex, GPT-5-based coding agent

**Work period:** September 28–29, 2026
**Scope:** Research, live Geoapify hotel search, synchronized Leaflet map,
verification, evidence, documentation, and checkpoint preparation. Persistent
shortlist behavior remained out of scope.

## Research and early design

The research prompt established that implementation must follow official
Geoapify Places and Leaflet documentation and one public list/map reference
before code changes. A representative excerpt was:

> “Begin Assignment 2 Part 1 research and early design only... Inspect the
> official Geoapify Places API documentation... Inspect the official Leaflet
> documentation... Create an early repository-native mockup.”

This produced `docs/assignment2-part1-research.md` and
`docs/mockups/assignment2-part1-early.svg`. The resulting decisions included a
strict 5 km filter, a 20-result limit, provider place IDs for shared selection,
honest missing-data handling, and visible provider/tile attribution.

## Dependency decision

The dependency check first proved that Leaflet was neither installed nor
declared. Installation was deliberately paused for approval. The approved
action was:

> “Approved. Add Leaflet 1.9.4 as an exact direct frontend dependency... Do not
> install any Vue Leaflet wrapper, TypeScript definitions, map plugin, or other
> package.”

Only `leaflet@1.9.4` was added to the frontend manifest and lockfile. Existing
`httpx` remained sufficient for backend provider requests.

## Backend implementation

The backend implementation prompt required a focused Places controller and a
combined local route:

> “Use category accommodation.hotel... filter=circle:{longitude},{latitude},5000
> ... bias=proximity:{longitude},{latitude} ... limit=20... Add GET
> /api/hotels/nearby?zip_code={zip_code}.”

This influenced `backend/app/places.py`, `backend/app/main.py`, and the focused
controller and route tests. The key remained in the backend configuration
helper, errors were sanitized, invalid features were excluded, and successful
empty results remained distinct from provider failures.

## Frontend implementation

The frontend prompt required one shared hotel identity across two views:

> “Implement the Assignment 2 Part 1 Vue nearby-hotel list, Leaflet map, and
> synchronized selection... selecting a hotel in either representation must
> identify the same hotel in the other.”

This influenced `NearbyHotelSearch.vue`, `NearbyHotelsMap.vue`, the nearby-hotel
API client, `App.vue`, and the application styles. It also preserved the fixed
ZIP demonstration, entered-ZIP lookup, Assignment 1 search, and booking history.

## Verification and evidence

The bounded smoke-test prompt authorized exactly one initial live nearby-hotel
search and required all other failure states to use local-only mocks:

> “Authorize exactly one live nearby-hotel search for ZIP 16802 through the Vue
> interface... Without consuming additional Geoapify quota, use temporary
> local-only mocked behavior...”

The observed live search returned State College and 20 provider hotels. The
test verified list/map synchronization, attribution, invalid input, empty,
unresolved, provider-failure, regression, and clean-console behavior. Detailed
expected-versus-observed results are in `docs/verification.md`.

## Failed or revised approach

The original evidence plan attempted to save all live screenshots and the
recording automatically. Browser tooling safely saved the validation state but
did not preserve suitable live and synchronized-selection frames after the
mock-state sequence, and it could not create the required demonstration video.
The approach was revised rather than fabricating or overstating evidence: the
normal application was restored, exact manual capture instructions were given,
and the student captured and reviewed the remaining files. A filename using
`live.hotels` was also normalized to the required repository filename
`assignment2-part1-live-hotels.png` without altering the original Desktop file.

This revision is reflected in `evidence/README.md`, which records the reviewed
files, dimensions, and SHA-256 hashes.
