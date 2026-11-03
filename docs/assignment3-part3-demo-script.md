# Silent recording A — finished application demonstration

Prepared November 2, 2026. **Script only; no recording has been created or reviewed.**
Aim for roughly 5–7 minutes, adjusting for readability. The assignment specifies
no video length. Use fictional data, mocks and the already verified isolated copy.
No installation or paid call is needed for recording. Preserve original databases.

## Prepare the screen

1. Close personal tabs, notifications and unrelated windows. Use a browser zoom
   at which the top Crisis support/Leave controls and exercise fit visibly.
2. Use the existing verified folder:
   `/private/tmp/hudson-part3-setup-20261102`. It is an unpublished snapshot,
   not a committed clean checkout. If it is missing, stop and request a new
   isolated recording setup; do not switch to original databases or install.
3. Check that ports 8000/5173 are free before starting. If occupied, request
   assistance identifying their owner; do not stop unrelated services.
4. In Terminal A, run these lines, leaving it open:

   ```bash
   cd /private/tmp/hudson-part3-setup-20261102
   SKILLS_MODEL_MODE=mock backend/.venv/bin/uvicorn app.main:app --reload --reload-dir backend/app --app-dir backend
   ```

5. In Terminal B:

   ```bash
   cd /private/tmp/hudson-part3-setup-20261102/frontend
   npm run dev
   ```

6. Open `http://localhost:5173/#skills`. Use this exact hostname throughout the
   recording; it matches Vite's verified local address. Do not click ZIP lookup,
   nearby-hotel, advisor or external support links. No .env/key is needed.
7. Open a second browser tab with this local caption file:

   ```text
   file:///Users/natehudson/Documents/ChatGPT/hudson-travel/assignment3/part3/recording-cards.html#demo-01
   ```

   Use Previous/Next or the card selector; show each caption for about 8–12
   seconds. These are prepared text cards, not actual result evidence. For an
   exercise, show the caption **before** Start; keep the exercise tab foreground
   until finished. Switching tabs/minimizing pauses the actual app.
8. Press **Command–Shift–5 → Record Selected Portion**. Select the browser content
   plus tabs, excluding personal desktop content. In **Options**, select
   **Microphone → None** and a known Save To folder. Click **Record**. Stop with
   **Command–Control–Escape** or the menu-bar stop icon. No audio is required by
   this script; readable captions and source explanations carry the meaning.

Caption-card visual review is pending: the browser tool blocks local file
preview. Open the file normally from Finder in a browser that permits local
files. If unavailable, use the script's caption text in a readable editor pane
between segments; do not bypass a browser warning. Keep the exercise foreground
for its entire active sequence regardless of caption method.

## Exact action sequence and silent explanations

| Segment | On-screen action | Caption / evidence to hold visibly |
| --- | --- | --- |
| Opening | Show card `demo-01`, then the Skills screen. | Fictional coursework, mock mode, no therapy/monitoring claim. |
| Research/design | Show `demo-02`, return to Skills. Click **Simpler view**, show that optional conversation/history disappear while Start/Crisis support/Leave stay. Click **Show more**. | User chooses contraction; no detector. R2/R3/R4, D1/D2/D3/D4. Do not start yet. |
| Save and reuse | Show `demo-03`. In Skills choose **Pacing display → Static cue**. Click **Simpler view → Save display choices**. Wait for the saved notice, then reload once with **Command–R**. | Reload returns to full view/device setting and merely offers the saved setup. |
| Explicit control | Click **Use last setup**. Show current simpler/static choices and Start still waiting. Click **Show more** so conversation/history options return; this changes the current simpler toggle without silently resaving it. | Reuse applies only display choices. Compact save/reuse/reset in simpler ready view is the documented D1/D5/R4 tradeoff. |
| Before conversation | Show `demo-04`. Click **Optional conversation before breathing**. Type exactly `Fictional demo: does this character need to type during breathing?` Click **Send fictional message**. Hold the **Mock responses only** disclosure and saved fixed reply. Click **Continue to breathing without waiting**. | This demo is a fixed mock, not evidence that a live model interpreted the message. Actual selection evidence is in the separate live report. |
| Complete skill | Show `demo-05`, return to the app. Click **Start 60-second exercise** once. Keep the browser foreground and do not type, switch tabs, pause or open support during this run. Let six cycles finish. | Record the complete sequence in real time. Static shape plus phase/count still carries pacing. Do not speed up or cut the sequence while implying it is continuous. |
| Actual timing | Open **Session timing details**. Hold the rendered interval, clock time, setup and phase count. Wait for **Latest checkpoint saved**. | Expect six cycles/twelve cues, but read the actual values shown. New setup time includes your choices/conversation since ready-view creation; do not substitute the earlier 17.146 s or promise an exact 60.000 s. If interrupted or delayed, describe it honestly and request help rather than relabel it complete. |
| After conversation | Click **Optional conversation after breathing**. Type `Fictional demo: this character dislikes moving cues.` Click **Send fictional message**, hold the labeled mock and static-option text. Click **Back to exercise options**. | Conversation is optional and outside pacing; a reply does not save/apply preferences. |
| Session/history | Show `demo-06`. Return to the app and click **Session history**. Open the completed entry created during this recording, identified by its displayed date/time. Show active/setup/pause/support times and expand **Saved checkpoints**. | These are client-reported acknowledged records, not independently verified clinical outcomes. Older temporary sessions may also appear; select this recording's entry. |
| Reload persistence | Reload once, then click **Conversation history**. Open the newest **after breathing** conversation and then the recording's **before breathing** conversation. Show both saved text pairs. | Reopening history makes no model call and does not start an exercise. Reload returns to ready; it does not resume the completed run. |
| Reset vs deletion | Click **Back to exercise options → Reset display choices**. Wait for the saved-clear notice. Click **Session history**, reopen the completed entry to show it remains. Open **Clear saved skills history**, show its separate confirmation, then **Cancel**. Click **Back to exercise**. | Reset is display-only; history deletion is a separate confirmed action. Do not click Clear permanently for this recording. Prior evaluation already tested real deletion/late-write protection with temporary data. |
| Interruption/support | Show `demo-07`. Return to the now-ready exercise, Start a second short run, wait a few seconds, click **Pause → Crisis support**. Hold the locally bundled U.S. panel; do not click/contact any service. Click **Back**, show **Paused**, then explicitly **Resume → Stop**. | This second run is deliberately stopped, separate from the complete run. Support return cannot resume for the user. |
| Leave and limits | Click **Leave**; hold **You have left the experience / Nothing else is required**. Show `demo-08`. | Prior evaluation/live findings and seven unresolved moderate lint-tool findings; no clinical-effectiveness claim. End recording. |

## Save and check

Save/rename as `assignment3-part3-demo.mov` (or an actual MP4 export). Watch it
from beginning to end: captions readable, one entire completed sequence visible,
timing readable, mock disclosure visible, no personal/credential content, support
and stopped/left states understandable. Do not infer success from this script.
Record filename, actual duration and hosting URL only after the file exists.
If editing, distinguish caption/evidence cuts from the uncut exercise.

Leave the services running only if immediately recording B; otherwise stop
**only Terminal A and B from this setup** with Control–C. Never stop an unrelated
service. No upload, public hosting, commit or submission is authorized by this guide.

Next recording: [process and generated-code script](assignment3-part3-process-script.md).
