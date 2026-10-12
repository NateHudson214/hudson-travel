# AI-use disclosure

Status: Assignment 3.1 disclosure, updated October 12, 2026. The student reported
the drafting model as **GPT-6.1 Sol**, with **medium** reasoning effort. Desktop
app version is unavailable in this record; add it if readily visible, otherwise
retain that limitation rather than inventing a version.
This disclosure covers the documented Assignment 3.1 design work; it does not
claim to be a complete retrospective inventory of Assignments 1 and 2.

## Tools and roles

| Tool | Identifier/version | Role in this milestone |
| --- | --- | --- |
| OpenAI Codex desktop assistant | GPT-6.1 Sol, medium reasoning effort (student-reported October 12, 2026); desktop app version unavailable. | Read the assignment and repository; propose scope, experience flow, technical records, model boundaries, research mappings, and documentation; check documentation and existing regression checks. |
| Assistant workspace tools | exec_command and apply_patch; exact tool version unavailable. | Read existing source files, write Markdown documentation, and run verification without installing dependencies. |
| Assistant web tool | web.run; exact tool version unavailable. | Inspect official resource pages and record source-verification limits. |
| Local helpline lookup | hotline.get_local_hotline; exact tool version unavailable. | Retrieve listed U.S. helpline contacts for proposed resource documentation. No call, text, or service chat was initiated. |

No image generator, AI-created raster asset, external clinical dataset, or
sub-agent was used for this milestone. The Mermaid flow and text sketch are
assistant-generated design artifacts. No skills-app provider call was made.
Assistant drafting itself is AI use; it is separate from the app's live model
integration, which does not exist yet.

The student supplied the assignment and complete research table, chose paced
breathing and optional before/after conversation, and confirmed same-repository
organization, a separate database, U.S. resource scope, and constrained replies.
The assistant proposed designs and tradeoffs; student review and final
submission decisions remain the student's responsibility.

## Existing provider configuration is not milestone use

The repository contains pre-existing OpenAI/OpenRouter clients and configured
model names from earlier hotel work. Reading those files does not establish
which model generated this chat or imply those models were called for Part 1.
Do not substitute an app backend default for the Codex drafting model identifier.
Earlier assignment tools/models and live runs are described in their existing
documentation and should be disclosed separately if a cumulative report is
required by the instructor.

## Review and unresolved items

- Drafting model/effort is recorded from the student's report; add desktop version
  if available. Unavailable tool versions are explicitly labeled above.
- Review the generated documents against the assignment before accepting them.
- Keep code reuse claims marked as planned until actual implementation occurs.
- Maintain this disclosure when tools/models change in later milestones.
- Record measured testing, failures, and live calls separately from proposed
  checks. See the [curated log](evidence/assignment3-part1-log.md).
