# Part 1 Hotel-Search Screenshot Evidence

**Status:** Corrected screenshots captured and reviewed September 10, 2026. The
earlier city-search images were removed because they did not demonstrate the
authoritative requirement.

- `part1-hotel-search.png`: 2878 x 1696 PNG showing `Harbor Lantern Hotel` and
  the complete T001/T009 result table. SHA-256:
  `d58cbe7f37151ebf361976357a19b06552c4733059dc285a0d1f9d565a6c7b11`.
- `part1-hotel-no-results.png`: 2878 x 1696 PNG showing `Not a Real Hotel`, the
  clear no-results message, and no table. SHA-256:
  `be7c45e845f4b7249665c48f550c68b2b2f05b5335e2b23d68c6bca4fad8457b`.

Both images contain only the Hudson Travel application and expose no browser
chrome, account names, Codex UI, terminals, desktop content, or private data.

The images were captured with this procedure after the corrected browser smoke
test passed:

1. Start the backend from the repository root:

   ```bash
   backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```

2. Start the frontend from `frontend/`:

   ```bash
   npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
   ```

3. Open <http://127.0.0.1:5173>. Do not open `frontend/index.html` with a
   `file://` URL.
4. Search `Harbor Lantern Hotel`. Confirm the table shows exactly `T001` and
   `T009` with the correct hotel, city, state, dates, and nightly rate. Capture
   only the application page and save it as:

   ```text
   evidence/part1-hotel-search.png
   ```

5. Search `Not a Real Hotel`. Confirm a clear no-results message appears and the
   table is absent. Capture the same application-only region and save it as:

   ```text
   evidence/part1-hotel-no-results.png
   ```

6. Open both images and confirm the text is readable and no browser chrome,
   account names, Codex UI, terminals, desktop content, or other private material
   is visible.
7. Stop both services with **Control-C**.

## Assignment 2 Part 1 live hotel-search evidence

**Status:** Captured and reviewed September 29, 2026. The student confirmed
that all four files are readable, demonstrate the required live search,
synchronized selection, attribution, and validation behavior, and contain no
API key, secret, private information, or unrelated content.

- `assignment2-part1-live-hotels.png`: 2876 x 1696 PNG showing ZIP `16802`,
  the State College search center, 20 provider hotels, the Leaflet map, and
  attribution. SHA-256:
  `77fde335139eb798d759f5fd4c41e3450e1a20219e5e1aac93c7a7f41b04232d`.
- `assignment2-part1-selection.png`: 2870 x 1692 PNG showing Hotel State
  College selected in the list and the matching map popup. SHA-256:
  `f0005dbea808d5423e6ea61678c61af8e256ac6a7fb2c95b78884cdaf85a1197`.
- `assignment2-part1-states.png`: 914 x 720 PNG showing five-digit ZIP
  validation with no stale hotel result. SHA-256:
  `2b08b1eb9f2442487f4359d9a35798a0fa06b63fff834aa4ef5e9accbefdbbc3`.
- `assignment2-part1-demo.mov`: 47,870,865-byte QuickTime demonstration
  recording reviewed by the student. SHA-256:
  `3ff4516cd2692745703255f0718898835d85ac521dd0c8b1af649401f3b38b17`.

Only the retained Hudson Travel backend and frontend were stopped after capture;
ports 8000 and 5173 were confirmed free.

The reviewed evidence is preserved in implementation checkpoint
[`0f38ae0ac35808e332ec91472bb0d5393e5adfc8`](https://github.com/NateHudson214/hudson-travel/commit/0f38ae0ac35808e332ec91472bb0d5393e5adfc8)
and its non-fast-forward `main` merge
[`6739c4e5b4e4a93b74d6558253078024b1aa7cbf`](https://github.com/NateHudson214/hudson-travel/commit/6739c4e5b4e4a93b74d6558253078024b1aa7cbf).

## Assignment 2 Part 2 local-hotel evidence

**Status:** Captured and reviewed October 5, 2026. The student confirmed that
all three files are readable and contain no API key, secret, private
information, or unrelated content.

- `assignment2-part2-edited-rate.png`: 2880 x 1696 PNG showing the ZIP `16802`
  **Saved locally** result, Hotel State College, and the edited October 12
  `$125.50` rate with 7 rooms. SHA-256:
  `90eea9cdd5f6f1360842219281e8f0e12335f7c1bd264610a71d373fb04469de`.
- `assignment2-part2-local-first.png`: 2858 x 1476 PNG showing the saved-local
  interface and Safari Network evidence for the local `saved-hotels` request,
  with no `/api/hotels/nearby` request in the captured list. SHA-256:
  `f49cf3440b34cb33273b4160950fa2673bf7eceb375e61b52e4ef3986ae1f543`.
- `assignment2-part2-database.png`: 2880 x 1792 PNG showing exactly five Hotel
  State College rows for October 10–14, including `12550` cents and 7 rooms on
  October 12. SHA-256:
  `0e6f05ee5de5ddbe5831b7edf68ee722491bda48b58f71e6cdf8a592e1581798`.

Only the Hudson Travel services used for evidence capture were stopped after
review, and ports 8000 and 5173 were confirmed free.
