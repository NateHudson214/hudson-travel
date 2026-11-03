# Silent recording B — actual failure, evidence, decision and generated code

Prepared November 2; recording update November 3, 2026. **Actual B now exists and is sample-reviewed; final hosted access remains unverified.**
Aim for roughly 4–6 minutes; the assignment specifies no duration. This is a
read-only walkthrough of actual saved Part 3 evidence and current source, not a
live-model rerun or a staged claim of a new failure. No server is needed.

Latest [media review](assignment3-part3-media-review.md): the student accepts A
framing as-is; the supplement below is no longer required. Actual B begins with
the thirteen-page walkthrough. The original preparation instructions remain for
reference; do not treat them as proof of a captured supplement.

## Simplified route for the recorded demo A — November 3 update

Video A now exists at `/Users/natehudson/Desktop/assignment3-part3-demo.mov`.
Sampled review: 307.345 seconds, 2866x1494, no audio track. The timing screen
shows 60.02 rendered /60.01 clock seconds and 56.26 seconds setup. It has useful
completion/history/support/Leave evidence, but the recorded region excludes the
fixed bottom Pause/Resume/Stop bar. Keep it; supplement those controls at the
start of B. This does not require repeating the full exercise or a live call.
[Review and limits](../evidence/assignment3-part3-media-review/video-a-review.json).

A single [process walkthrough](../assignment3/part3/process-walkthrough.html)
now embeds actual saved evidence and current generated-code excerpts. It has
13 pages with written explanations, source labels and suggested hold times.
Its source excerpts/fingerprints and JavaScript syntax were checked; browser
visual preview remains manual because local-file preview is blocked in the
browser tool. Read the explanations yourself before recording; ask about any
code you cannot explain. It is a prepared document, not a video or a test rerun.

1. Keep the already running isolated/mock app open. Open another tab in your
   normal Safari/Chrome browser with:

   ```text
   file:///Users/natehudson/Documents/ChatGPT/hudson-travel/assignment3/part3/process-walkthrough.html#1
   ```

   Preview readability and navigation before recording. Use Next/Right arrow to
   advance, Previous/Left to go back; the dropdown jumps to any page. If needed,
   enlarge the window or scroll slowly to expose code; do not make it unreadably
   small. Return to page 1, then switch to the app tab.
2. Hide unrelated/private content and notifications. Press **Command–Shift–5**.
   Choose **Record Entire Screen** so the bottom controls cannot be cropped out.
   Set **Options → Microphone → None**, **Save to → Desktop**, then **Record**.
   If using a selected portion instead, it must include the entire browser
   viewport down to its very bottom, including fixed Pause/Resume/Stop controls.
3. Record a **short stopped session**: Start, wait a few seconds, Pause, open
   Crisis support, Back, visibly hold Paused/Resume/Stop, explicitly Resume,
   then Stop and Leave. Keep the entire bottom bar in frame. Do not click/contact
   a resource link. This is a supplemental control demo, not a second full
   completion or a recreated provider failure.
4. Switch to the walkthrough tab at **page 1**. Leave it visible for 10 seconds.
   Advance through all **13 pages**, holding each for the time shown at bottom
   right. Show the code as well as its explanation. The walkthrough covers:
   actual initial failure → reproduction → mapping repair/missed multiline patch
   → passing verification → application-owned timing → paused support return →
   reviewed reply rendering → bounded provider wait → real live results → limits.
   No additional file opening, command, installation or model call is needed.
5. Hold the last page for about 35 seconds. Stop with **Command–Control–Escape**.
   Save/rename the actual file `assignment3-part3-process.mov`.
6. Watch B and A in full: bottom controls now readable, source snippets/captions
   readable, failure distinguished from a new test, real timeout retained,
   unresolved seven moderate findings disclosed, no personal/secret content.
   Provide the actual B file for review. No hosting/upload is authorized here.

The detailed source-by-source route below remains an alternative; do not record
both routes unless desired. No completed B recording is claimed.

## Recording setup

Open the caption tab at:

```text
file:///Users/natehudson/Documents/ChatGPT/hudson-travel/assignment3/part3/recording-cards.html#process-01
```

Open the files below in Codex or your editor. Increase text size so the selected
code and error lines are readable. Use Command–F to find the exact function/text
named below. Do not display .env, whole personal terminal histories, real keys,
original databases or raw provider output. Only the curated files listed here
are needed. Use Command–Shift–5, Record Selected Portion, Microphone None, Record.
Show each caption for about 8–12 seconds; then show its matching evidence/code.

Caption-card visual review is pending: the browser tool blocks local file
preview. Open the file normally from Finder in a browser that permits local
files. If unavailable, use the script's caption text in a readable editor pane
between segments; do not bypass a browser warning. Keep the exercise foreground
for its entire active sequence regardless of caption method.

## Exact sequence

1. Show **process-01**. State on screen that the first failure is saved historical
   evidence from the fresh setup and that this walkthrough makes no new call.
2. Show **process-02**, then open
   [initial backend output](../evidence/assignment3-part3-setup/backend-tests.txt).
   Find `has no attribute 'skills_database_path'`, hold the fixture traceback,
   then find `362 passed, 130 errors`. This is the actual earlier failure.
3. Show **process-03**, then
   [minimal reproduction](../evidence/assignment3-part3-setup/pytest-reproduction.json).
   Hold `before: true`, `during: true`, `after_undo: false` and the recorded
   pytest/Starlette versions. Explain visually that the missing setting followed
   cleanup; it was not evidence that production startup could never work.
4. Show **process-04**, then open
   [corrected session fixture](../backend/tests/skills/test_sessions.py).
   Find `Patch State storage directly`. Show the `monkeypatch.setitem` mapping
   patch, including the multiline clock setting. Explain: pytest stores/restores
   dictionary entries; this matches Starlette's dynamic storage. Production code
   and package versions did not need changing for this repair.
5. Show [first correction output](../evidence/assignment3-part3-compatibility/first-correction-tests.txt),
   search `skills_now_provider`, then `444 passed, 48 errors`. Hold briefly:
   one multiline patch was missed on the first correction. Then show
   [passing current backend output](../evidence/assignment3-part3-dependencies/backend-tests.txt),
   find `492 passed`, and [cleanup regression evidence](../evidence/assignment3-part3-compatibility/state-isolation-tests.txt),
   find `same_state_keys_and_original_bindings`. The latter is the separate
   diagnostic; do not describe it as the latest full-suite count.
6. Show **process-05**, then
   [application-owned timing](../frontend/src/skills/breathing.js).
   Explain these three regions while pointing to the actual code:
   - `BREATHING_SKILL`: 4000 ms inhale, 6000 ms exhale, six cycles. This module has
     no model/network input; the application owns the sequence.
   - `sample()`: monotonic elapsed deltas count actual active time; paused time
     is separated into support or other pause. Excess delay preserves the last
     cue and pauses rather than skipping. The 250 ms threshold is provisional.
   - `closeSupport()` / `resume()`: closing only clears the support flag; the
     explicit Resume action changes paused to running. Setup is measured by
     `start()` from ready-view creation, not cold download time.
7. Show **process-06**, then
   [reply renderer](../backend/app/skills/replies.py), find `def render_reply`.
   Explain the exact two-key shape, approved reply IDs, <=2 unique compatible
   fact IDs, and application-catalog rendering. The model cannot supply arbitrary
   visible therapeutic prose, change timing or press navigation controls.
   Then open [provider](../backend/app/skills/provider.py), find
   `TIMEOUT_SECONDS` and `asyncio.wait_for`. Explain one bounded request,
   finite three-second wait, sanitized category and no automatic retry.
   In [live lifecycle](../backend/app/skills/live.py), find `def finish`:
   it requires the matching history generation and an existing pending run before
   saving; it starts with the fixed fallback and only replaces it after validation.
   These are generated implementation pieces that the student can explain, not
   claims that a system prompt alone provides the safety boundary.
8. Show **process-07**, then the table in
   [actual repeated live results](assignment3-part3-live-checks.md).
   Hold typing timeout 3066 ms, typing success 1522 ms and the two identical motion
   selections. Explain: four dispatched attempts, no retry; the first timeout has
   no received selection/usage. Decision: keep finite waiting, allow continuation,
   preserve budget accounting; do not spend again to make the sample look perfect.
   Show [surprising Leave observation](assignment3-part3-evaluation.md), find
   `completed saved mock turn`. A late mock may save after local exit while the
   reply stays out of the abandoned UI; do not promise undo of dispatched work.
9. Show **process-08**, then
   [dependency results](../evidence/assignment3-part3-dependencies/results.json)
   and [readiness checklist](assignment3-part3-readiness.md).
   Explain four approved updates passed; seven moderate lint-tool findings remain
   unresolved, not student-accepted or fixed. Actual OS reduced-motion/CSS,
   screen-reader/full accessibility and device/load timing remain untested.
   Recorded software behavior does not establish clinical effectiveness.
10. End recording. Save as `assignment3-part3-process.mov` (or actual MP4 export).
    Watch the entire file. Verify failure → evidence → code correction → passing
    result → decision is readable, plus the pacing/reply code explanation.
    No video is considered complete merely because this script exists.

## Optional read-only terminal views

If the editor cannot make the result lines readable, these commands display only
curated public coursework evidence; use them from the repository root:

```bash
rg -n -m 2 "has no attribute 'skills_database_path'|362 passed, 130 errors" evidence/assignment3-part3-setup/backend-tests.txt
cat evidence/assignment3-part3-setup/pytest-reproduction.json
rg -n "444 passed|492 passed" evidence/assignment3-part3-compatibility/first-correction-tests.txt evidence/assignment3-part3-dependencies/backend-tests.txt
```

Do not run tests/provider requests during this walkthrough merely to produce new
results. Do not use the API key or original SQLite file as visual evidence.

After both recordings, provide the actual files for quality review before any
hosting/publication. [Submission checklist](assignment3-part3-readiness.md) lists
separate commit/access/link and Canvas steps. No uploads are made by this script.
