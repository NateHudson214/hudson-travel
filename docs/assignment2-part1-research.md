# Assignment 2 Part 1 — Research and Early Design

**Observation date:** September 28, 2026
**Stage when recorded:** Research and early mockup only. The live hotel search
and map shown in the mockup had not yet been implemented; later implementation
and verification are recorded in `docs/design.md` and `docs/verification.md`.

## Authoritative scope

Part 1 extends the completed five-digit U.S. ZIP lookup. FastAPI must first
resolve the requested U.S. postcode and then ask Geoapify for hotels within a
strict 5 km circle around that returned point. Vue must show those provider
results in a list and on a Leaflet map, with one shared selected hotel. The
interface must distinguish loading, invalid input, unresolved ZIP, no hotels,
and service failure.

The live response is location information, not inventory. Hudson Travel must
not invent prices, ratings, availability, rooms, or booking confirmations, and
must not claim that the returned set is exhaustive. The shortlist and new
persistence belong to Part 2 and are not part of this design slice.

## Sources and decisions

### Geoapify Places API

Sources:

- <https://apidocs.geoapify.com/docs/places/>
- <https://apidocs.geoapify.com/how-to/place-discovery/nearest-place-by-category/>
- <https://www.geoapify.com/places-api/>
- <https://www.geoapify.com/pricing/>

Useful findings:

- `accommodation.hotel` is the focused category for hotels. The broader
  `accommodation` category would also include apartments, chalets, guest
  houses, hostels, huts, and motels, which exceeds this assignment's hotel
  wording.
- A strict radius uses
  `filter=circle:{longitude},{latitude},5000`. A proximity bias uses
  `bias=proximity:{longitude},{latitude}` and orders results from the returned
  ZIP point. Longitude precedes latitude in both parameters.
- A filter constrains the results; a bias only affects ordering. Using both
  prevents a distant place from appearing while still producing a useful
  nearest-first list.
- The response is a GeoJSON `FeatureCollection`. Useful feature properties can
  include `place_id`, `name`, `formatted`, `address_line1`, `address_line2`,
  `city`, `state`, `postcode`, `country`, `lat`, `lon`, `distance`, and
  `categories`. Geometry coordinates are also available.
- `place_id` is the provider identity that can connect the list and marker and
  later support Part 2 without inventing a local hotel identity.
- The service permits a limit as high as 500, but returned features are billed
  in groups of 20. A 20-result limit is sufficient for a readable course map
  and keeps one search within the first Places credit band.
- The free plan currently advertises 3,000 credits per day and up to five
  requests per second. The interface should submit only on an explicit search,
  disable repeated submission while loading, and test quota/rate-limit behavior
  with mocks rather than consuming quota.
- Geoapify and OpenStreetMap attribution are required for Places data on the
  free plan.

Weaknesses and risks:

- Coverage and optional fields vary. A place can lack a name or complete
  address, so the interface cannot assume every field exists.
- A proximity bias by itself does not enforce 5 km.
- A high result limit increases visual clutter and credit use without proving
  that the response is a complete hotel inventory.
- Provider failures and quota responses are not successful empty searches.

Hudson Travel decisions:

- Request `accommodation.hotel` with a 5,000-metre circle filter, matching
  proximity bias, and `limit=20`.
- Treat the geocoded postcode point as the sole search center; never use browser
  geolocation or silently substitute another postcode.
- Return only a small backend-owned contract: provider place ID, optional name,
  optional formatted address, numeric coordinates, and optional distance.
- Exclude any provider feature without a stable `place_id` or valid numeric
  coordinates because it cannot safely synchronize the list and map.
- Render `Name unavailable` or `Address unavailable` when appropriate, rather
  than inventing values. Do not render price, rating, availability, or booking
  claims.
- Label results as “up to 20 hotels returned by Geoapify within 5 km,” not “all
  hotels.”
- Keep the API key and both Geoapify requests in FastAPI. No provider request or
  `VITE_` credential belongs in Vue.

### Leaflet

Sources:

- <https://leafletjs.com/examples/quick-start/>
- <https://leafletjs.com/reference>
- <https://operations.osmfoundation.org/policies/tiles/>

Useful findings:

- Leaflet requires its JavaScript and CSS and a map container with an explicit
  height.
- `L.marker([latitude, longitude])` uses latitude-first order, unlike the
  Geoapify filter parameters.
- Markers are interactive and keyboard-enabled by default. Marker `click`
  events can update the same selected place ID used by a list button.
- `fitBounds` can frame the search center and returned markers. A maximum zoom
  should prevent an excessively close view when there is only one point.
- A selected marker can use a distinct icon or z-index while the matching list
  card uses selected styling and `aria-current`.
- Tile layers must show their provider attribution. Leaflet's attribution
  control is enabled by default and collects layer attribution.
- OpenStreetMap's standard tile service permits ordinary human interactive
  viewing but is best effort, requires the HTTPS tile URL and visible
  attribution, and prohibits bulk download or prefetching.

Weaknesses and risks:

- Leaflet does not supply map tiles; choosing and attributing a tile provider is
  a separate responsibility.
- Missing Leaflet CSS produces a visibly broken map even if JavaScript works.
- Recreating maps or markers without cleanup can leak DOM state in a reactive
  component.
- Map-only selection can exclude keyboard and screen-reader users if no
  equivalent list control exists.

Hudson Travel decisions:

- Use Leaflet as a declared frontend dependency only after the dependency
  approval step.
- Use a focused Vue map component that creates one map, updates a marker layer,
  and removes the map during component cleanup.
- Keep `selectedPlaceId` in the Vue parent as the single selection source of
  truth. Both list buttons and marker events emit the same provider ID.
- Preserve keyboard access through list buttons and Leaflet's keyboard-enabled
  markers; never require a pointer-only map interaction.
- Use standard OpenStreetMap tiles only for normal local interactive viewing,
  with visible `© OpenStreetMap contributors` attribution. Do not prefetch or
  automate broad map movement. Keep the tile URL isolated so it can be changed
  later.
- Show separate `Powered by Geoapify` attribution beside the hotel results.
  Do not put the backend Geoapify key into a tile URL.

### Existing list-and-map interface: Expedia Hotels Near Me

Source:

- <https://www.expedia.com/hotels-near-me>

Useful interaction observed:

- The page places a destination search, an available-properties list, and a map
  in the same search flow. Property cards provide a strong textual identity
  while the map supplies spatial context.

Weaknesses or omissions for this project:

- The public page is dense with dates, traveler controls, imagery, promotional
  labels, prices, ratings, and availability messaging. Those elements would
  suggest booking capabilities and data that Geoapify does not provide.
- “Near me” can obscure which point is being used as the search center.
- A large commercial result page makes transient loading, empty, and failure
  states less prominent than this assignment requires.

Hudson Travel decisions:

- Adopt the paired list-and-map hierarchy and a strong visible selected state.
- Display the resolved ZIP and locality above the results so the center is
  explicit.
- Keep each hotel row compact: provider name, honest address, and distance when
  available.
- Omit commercial prices, ratings, availability, promotions, dates, and booking
  claims from live Geoapify results.
- Place status feedback before the list/map region and never render a map full
  of stale markers after validation or request failure.

## Proposed Part 1 interaction

1. The traveler enters a five-digit U.S. ZIP as text and selects **Search
   nearby hotels**.
2. Vue validates exactly five ASCII digits, clears stale live results, disables
   the ZIP controls, and displays a loading message.
3. FastAPI validates the ZIP, resolves that exact U.S. postcode, then requests
   up to 20 `accommodation.hotel` places inside 5 km of the returned point.
4. FastAPI returns the resolved center and sanitized hotel fields in one
   response, keeping the two provider calls and credential out of Vue.
5. Vue displays the resolved location, count/limit language, hotel list, and
   map. The first valid hotel may be selected initially.
6. Selecting a list row emphasizes and opens or focuses its marker. Selecting a
   marker emphasizes the same list row. Both paths set one `selectedPlaceId`.
7. A new search replaces the center, list, markers, and selection together.

## Proposed local API contract

```text
GET /api/hotels/nearby?zip_code=16802
```

Proposed successful response shape:

```json
{
  "location": {
    "postcode": "16802",
    "country_code": "us",
    "latitude": 40.803167822,
    "longitude": -77.861384958,
    "locality": "State College"
  },
  "radius_meters": 5000,
  "result_limit": 20,
  "hotels": [
    {
      "place_id": "provider-place-id",
      "name": "Example Hotel",
      "formatted_address": "Example address",
      "latitude": 40.8,
      "longitude": -77.86,
      "distance_meters": 420
    }
  ]
}
```

The example is a contract sketch, not a live-result claim. Optional provider
values may be `null`. A successful request can return an empty `hotels` list;
that state must remain distinct from invalid ZIP, unresolved ZIP, missing
configuration, provider failure, quota/rate limit, and malformed response.

## Planned responsibilities

| Layer | Part 1 responsibility |
| --- | --- |
| Vue view | ZIP form, status feedback, resolved-center summary, hotel list, map, attribution, and keyboard-visible selection. |
| Vue state/controller | One request lifecycle and one `selectedPlaceId`; replace list, markers, and selection atomically. |
| Frontend API client | Call only the local FastAPI route and convert safe backend errors into displayable messages. |
| FastAPI route | Validate the ZIP, orchestrate geocoding and Places lookup, and map internal failures to safe HTTP responses. |
| Python provider controller | Build finite-timeout Geoapify requests, validate exact U.S. postcode and Places data, and return a small internal model. |
| External data | Geoapify supplies the resolved point and nearby hotel features; OpenStreetMap supplies visible map tiles. |

## State inventory for verification

| State | Required behavior |
| --- | --- |
| Initial | ZIP input and Search action; no stale live results. |
| Loading | Clear progress text; conflicting ZIP controls disabled. |
| Results | Resolved center plus matching list and map markers. |
| Selected | The same provider ID is visibly identified in list and map. |
| Invalid | Five-digit validation message; no provider request or stale results. |
| Unresolved | Exact ZIP could not be resolved; no substituted search center. |
| No hotels | Successful resolved search with zero returned hotels. |
| Service failure | Clear failure message, not an empty-results message. |
| Quota/rate limit | Safe specific feedback tested with mocks, not repeated live calls. |
| Missing fields | Honest fallback or omission; no invented travel data. |

## Early mockup

The repository-native mockup is
[`docs/mockups/assignment2-part1-early.svg`](mockups/assignment2-part1-early.svg).
It is deliberately labeled as an early design and shows the primary desktop
results view plus all required alternate states. Implementation may revise
spacing and responsive behavior, but should preserve the state distinctions and
shared selection model.

## Dependency finding

- Backend: existing `httpx` is already installed and directly declared, so the
  researched Places request does not currently imply another Python package.
- Frontend: Leaflet is neither installed in `frontend/node_modules` nor directly
  declared in `frontend/package.json` or `frontend/package-lock.json`.
- The next step must use the course CHECK → TAKE ACTION → VERIFY loop and obtain
  student approval before adding Leaflet. No dependency was installed or edited
  during this research stage.
