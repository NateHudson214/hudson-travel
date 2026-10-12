# Project Rules

These instructions apply to the entire repository.

## Architecture

- Keep backend code in `backend/` and frontend code in `frontend/`.
- Keep the FastAPI application entry point at `backend/app/main.py`.
- Keep HTTP endpoints under the `/api` prefix unless an endpoint is specifically
  intended for infrastructure or documentation.
- Keep Vue components focused and place reusable components under
  `frontend/src/components/`.

## Development

- Do not commit virtual environments, `node_modules`, build output, secrets, or
  local editor settings.
- Add or update tests when behavior changes.
- Prefer small, focused changes and document new setup requirements in
  `README.md`.
- Do not install or upgrade dependencies unless the task explicitly requires it.
- Keep secrets out of source control; document required environment variables in
  an `.env.example` file.
- Treat the instructor-supplied CSV files in `backend/data/` as read-only inputs.

## Verification

- Run relevant backend and frontend checks before declaring a change complete.
- If dependencies are unavailable, state which checks could not be run.

## Assignment 3 Skills Prototype

- Keep Assignment 3 as a separate view in this repository with its own database;
  preserve existing travel behavior and course CSVs. Keep the FastAPI entry point
  and frontend/backend layout described above.
- Part 1 is documentation-only unless the student explicitly requests an
  implementation experiment. Read docs/assignment3-part1-plan.md,
  docs/assignment3-part1-experience.md, and docs/assignment3-part1-technical.md
  before developing the skills experience. Clearly label proposals and
  distinguish measured results from design targets.
- Initial skill: six cycles of four-second inhale and six-second exhale, targeting
  60 active seconds. Keep the reviewed sequence in application-owned context.
  Do not let a model change the skill, timing, navigation, or saved preferences.
- Conversation is optional before/after breathing. The selected model boundary
  is reviewed reply IDs and approved fact IDs, rendered by the application;
  arbitrary model-written therapeutic prose is not an approved output.
- Keep Crisis support, Leave, and relevant Pause/Stop controls available during
  loading, failures, simpler view, and exercises. U.S. resource information must
  be labeled and independently bundled, not gated by a model or detector. Read
  docs/assignment3-part1-resources.md; reverify contacts before implementation.
- Use only fictional scenarios. Do not diagnose, claim therapy or monitoring,
  or offer/deploy/link the prototype as support for a real person in distress.
  Do not contact crisis services as a coursework test.
- Default tests and peer sessions to mocked responses. Live peer-testing calls
  require host selection and a durable budget of at most fifty dispatched calls;
  return to mock mode at the limit. No live calls are part of Part 1.
- Record timing from first exercise instruction through final planned step,
  including application delays. Report setup separately; exclude user-chosen
  pauses and crisis-resource access. Do not force users to leave at a deadline.
- Retain AI-USE.md and curated, redacted evidence. Never fabricate observations,
  failures, recordings, model identifiers, or submitted commits. Each milestone
  needs its own report.md; use assignment3/part1/report.md for this milestone
  without overwriting earlier reports.

## Course Macros

The existing macros below verify Hudson Travel. A skills-specific verification
procedure must be defined when the skills application is implemented.

### AutoLoop

Trigger: When the user says "AutoLoop", perform a bounded fix-and-verify loop.

1. Read `AGENTS.md`, `README.md`, and the relevant verification instructions.
2. State the acceptance check for the current task.
3. Run the smallest relevant check.
4. If the check fails for an in-scope source-code reason, inspect the evidence,
   make the smallest relevant correction, and rerun the check.
5. Repeat for no more than five correction cycles.
6. Stop early and ask for direction if the next action requires a dependency
   change, machine-level permission, destructive action, an unrelated process to
   be stopped, or broader scope.
7. Report every cycle, the final evidence, and anything not verified.

### SmokeTest

Trigger: When the user says "Run the smoke test", verify the working application
without changing source code or dependency declarations.

1. Read `AGENTS.md`, `README.md`, and `docs/verification.md`.
2. Run the backend pytest suite.
3. Run the frontend API-client tests, lint, and production build.
4. Check the intended backend and frontend ports. Never stop an unrelated
   process.
5. Start only the backend and frontend processes needed for this test in
   Codex-managed terminals.
6. Verify successful, unmatched, and blank-hotel-name API requests.
7. Use automated browser control to verify `Harbor Lantern Hotel`, lowercase,
   surrounding-space, partial-name, `Not a Real Hotel`, and blank-hotel-name
   searches against the acceptance behavior in `docs/verification.md`.
8. Confirm table values agree with the joined CSV records and that validation or
   request errors clear stale results.
9. Confirm that the browser displays no application error and report any UI
   behavior that could not be tested.
10. Unless the user asks to keep the app running, stop only the processes created
    by this smoke test.
11. Report concise evidence from tests, builds, endpoints, every automated UI
    interaction, and service cleanup.

### Combined Trigger

When the user says "AutoLoop: run the smoke test", run the SmokeTest macro. If an
in-scope check fails, use the AutoLoop rules to make the smallest correction and
repeat the smoke test until it passes, five correction cycles are exhausted, or
a stopping condition is reached.
