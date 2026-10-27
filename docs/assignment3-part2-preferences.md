# Assignment 3 Part 2 — Explicit saved display choices

Implemented and verified October 26, 2026. Coursework with fictional data only;
no live model calls or dependency changes. This is one implementation step, not
a final Part 2 submission or clinical-effectiveness claim.

## Experience and research tradeoff

The ready breathing screen offers Save display choices, Use last setup when one
exists, and Reset display choices. The two choices are simpler view on/off and
motion mode system/static/gentle. Save records the current choices only after an
explicit click. Changing a control, starting/completing/stopping an exercise, or
receiving a mock reply never saves a preference automatically.

Full page entry starts with the full view and device motion setting. A read of
saved choices offers a preview without applying it. Use last setup applies only
the two display choices, leaves the engine ready, and requires a separate Start
click. Current manual choices remain while navigating the cached view; reload
returns to defaults and offers reuse. This is a convenience based on explicit
choices, not an inference that an exercise helped or was preferred (D5/R4).
The extra Save click makes persistence explicit at the cost of one additional
action compared with the Part 1 proposal to remember changed controls.

Reduced motion always overrides a saved gentle preference for actual rendering;
the stored setting itself remains the user's choice. Simpler view contracts
secondary explanations/refresh controls while retaining the choice preview,
Save/Use/Reset, and error recovery. Crisis support and Leave stay outside this
panel. Exercise Pause/Stop controls remain unchanged. No display-choice controls
are inserted into the atomic breathing sequence.

Reset immediately restores full view/device motion locally, then clears the saved
setup. It never deletes history, stops/starts an exercise, or changes the fixed
sequence. During storage failure the local reset still works and the error says
the saved copy may remain. Refresh reads the current saved copy without applying
it; an explicit reset can clear it after recovery. No automatic retry or forced
navigation occurs. Pending choices never block Start, crisis access, or Leave.
Requested writes may finish after leaving, but late results never change the
current exercise or reopen a view.

## Backend storage and contracts

The existing separate skills SQLite database now uses schema version 3 with one
additional table, skills_preferences. It contains one constrained singleton row:
revision, has_saved flag, simpler_view, motion_mode, updated_at, last_request_id,
and last_payload_json. Default/reset values are false/system with has_saved=0.
There is no account, emotional score, inferred preference, extra skill/timing
configuration, or provider setting. All browsers using this local backend share
the row; it is not an authenticated or encrypted personal profile.

Explicit transactional migrations support v1→v3 and v2→v3, validate required
legacy session/conversation columns before changing schema, retain all existing
sessions/events/messages/runs, and update both version markers. Foreign, partial,
newer and invalid schemas remain rejected. The API does not touch travel tables,
travel startup, instructor CSVs, or existing travel endpoint behavior.

| Route | Contract |
| --- | --- |
| GET /api/skills/preferences | preferences: revision, updated_at, and last_setup (null or simpler_view/motion_mode). No choice is applied by this read. |
| POST /api/skills/preferences | Strict body: request_id UUID, expected_revision nonnegative integer, action save/reset, display_settings. Save requires settings; reset accepts null/omitted settings only. |

Save example (illustrative only):

```json
{
  "request_id": "d13318bf-9491-4e67-b6b1-f6b755d84c72",
  "expected_revision": 0,
  "action": "save",
  "display_settings": {"simpler_view": true, "motion_mode": "static"}
}
```

Every accepted write advances revision. Responses include preferences and replayed.
An exact retry of the latest write returns the existing state without advancing
revision; changed data under that latest request ID fails 409. Older writes fail
409 once a newer save/reset exists, including an old save retried after reset.
The reset tombstone retains revision even with no saved setup, so a delayed save
cannot resurrect cleared choices. Conflicting tabs must refresh and explicitly
choose again; no silent merge or retry. Invalid controls/types/extra fields fail
422; storage errors are sanitized 503 responses.

The frontend serializes requested writes. Reset applies locally immediately,
queues behind an already dispatched save, reads a fresh revision, and then clears
the saved setup. It abandons any failed older save retry. Explicit retries reuse
the same body/UUID. A refresh clears a failed request only after a successful read,
then the user can make a new decision. Queues are in memory, not durable browser
storage. The backend contains no timer, navigation, or model control in this API.

## Verification

Final checks passed: **448 backend tests**, **74 frontend tests**, both non-fixing
frontend linters, production build (50 modules), local document links, and
`git diff --check`. Two existing backend dependency deprecation warnings remain.
Eighteen added backend cases use temporary databases and check defaults, strict
contracts, exact/stale retries, reset rollback, concurrent writes, persistence,
v1/v2 migration compatibility, partial legacy schemas/missing preference records, unchanged history, and
travel isolation. Seven added frontend cases cover API routing and the preference
controller, explicit application only, reduced-motion precedence, delayed reads,
write ordering, retry identity, reset failure, and disposal.

Backend command (repository root):

```bash
PYDANTIC_DISABLE_PLUGINS=__all__ PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest backend/tests -q
```

Frontend commands (frontend/):

```bash
npm test
./node_modules/.bin/oxlint .
./node_modules/.bin/eslint . --no-cache
npm run build
```

Normal startup was successfully verified, resolving the previous step's Uvicorn
file-read limitation. From the root, with the existing environment active:

```bash
uvicorn app.main:app --reload --reload-dir backend/app --app-dir backend
```

From frontend/, run `npm run dev`, then open `http://localhost:5173/#skills`.
The original broad reload watcher successfully started, but cloud dependency
hydration caused repeated reloads. The README command now watches backend/app
only, avoiding dependency/test/frontend changes. The final normal startup used
the existing venv executable with no plugin-disabling variable, protocol override,
custom ASGI bridge, provider fixture injection, or alternate database path.
No live-model endpoint was invoked. Existing credentials were not viewed/copied.

Observed browser checks:

- Saved simpler/static choices; reload showed full/system current choices and a
  saved preview. Use last setup applied simpler/static while data-status remained
  ready. Only a separate Start began pacing; data-static-cue was true.
- Opened crisis support during the exercise; returning stayed paused. Stop saved
  one fictional session and four events. Reset later retained that history.
- Stopped only this task's backend, reset locally, opened crisis support, and
  used Leave despite remote storage failure. A stale “clearing” notice initially
  remained after failure; corrected notice handling and repeated the case. Final
  failed state shows only the error, not continuing progress.
- Restarted the normal backend. Refresh showed the saved copy still existed after
  the failed reset, without applying it. Explicit reset cleared it. Reload showed
  full/system and no saved setup. Repeated compact-view save/reuse/reset confirmed
  the final UI; persisted row ended at revision 4 with has_saved=0.
- Session history remained available. Database comparison across reset was
  byte-for-byte equal at the row-content level for sessions/events/conversations/
  messages/runs. Browser had one fictional session; conversation preservation was
  tested with temporary database records in the backend suite.
- Travel returned T001/T009 for Harbor Lantern Hotel and disabled offered-stay
  selection after Not a Real Hotel. No booking/provider actions were used.
  Travel SHA-256 before and after skills/browser checks was unchanged:
  984f739427049ddf1454d78cc26ce36179477936ef290f0ecece9a2a79a1108b.
- Final browser warning/error log was empty after reload. Expected proxy failures
  occurred during the deliberately stopped-backend case. Normal services and
  their reloaders were stopped after testing; pre-existing user tabs were retained.

Evidence: [reuse without starting](../evidence/assignment3-part2-preferences/reuse-ready.jpg),
[persisted reset](../evidence/assignment3-part2-preferences/reset-persisted.jpg),
[failed remote reset](../evidence/assignment3-part2-preferences/reset-local-error.jpg),
[independent crisis access](../evidence/assignment3-part2-preferences/crisis-reset-failure.jpg),
[curated state/isolation checks](../evidence/assignment3-part2-preferences/records.json).
The browser used the normal ignored development skills database, initially absent;
its fictional stopped session remains for history review. No SQLite file is
included in evidence/source control. Timestamps in the curated data are UTC;
the user-facing verification date above is America/New_York.

## Remaining limits and next step

The actual OS reduced-motion preference was not toggled, and no screen-reader or
full accessibility audit was performed. Logic tests and the CSS override cover
reduced motion; static cues were observed. No new complete exercise duration,
clinical result, live-model quality, peer test, clean-checkout run, commit, push,
upload, or final Part 2 report is claimed. The resource lookup was rechecked and
matched the bundled U.S. contacts; no crisis service was contacted.

Confirmed Clear saved history remains separate work. It needs protection against
pending/dispatched conversation writes recreating deleted records, while keeping
explicit preference reset separate. Live integration/budgeting and final course
evaluation also remain unfinished. No broader implementation step began here.


Follow-up: [confirmed history clearing](assignment3-part2-clear-history.md) is now
implemented with schema v4, preserving this singleton and its revision. The
remaining-clear-history paragraph above describes the state of the preference
step, before that continuation.
