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
