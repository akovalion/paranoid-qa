---
name: test-cases
description: Test case authoring per QA best practices, with CSV export for Zephyr Scale import (Option 1) or direct creation via your TMS MCP. Use when the user asks to generate, write, or prepare test cases, checklists, or CSV for TMS import.
allowed-tools:
  — Read
  — Write
  — AskUserQuestion
---

Write test cases per the rules below. First prepare them in an md file for validation, then produce the CSV for import (or create directly via MCP, section 13).

Account for the requirements logic and existing mockups. On mismatch between mockup and implementation — log a question for the analyst.

1. Test case format:
   — Name — short and clear (object: essence of the check, e.g. "Calendar
     opening", "List pagination"). No URLs, selectors, or technical details
     in the name (they belong in steps/objective). Do not put TC-(test case number) in the name.
   — Test case preconditions (if applicable)
   — Steps (maximally detailed, atomic)
   — Expected result (state it only after logically significant steps)
   — Priority (High / Normal / Low)
   — Type (UI / Functionality / Integration — or the values used in your project)
   — Reference (link or mockup name from Figma/PDF, specific element) — if applicable
   — Use the EXACT names of fields, buttons, headings,
     placeholders as in the implementation/mockups/spec
   — If the mockup labels a field "Issued by?" — write "Issued by?",
     not "Issued by (ID document)"
   — Check: colons, question marks, letter case,
     spaces in labels
   — If names differ between requirements and mockups -
     log it as a question for the analyst

2. Steps:
   — One action per step
   — Always spell out:
     • "Click the "Button name" button"
     • "Enter the value "…" in the "Field name" field"
     • "Select the value "…" from the "Name" dropdown"
     • "Hover over the "…" element"
     • "Open the page at URL …"
   — Avoid shorthand references:
     ❌ "similarly", "repeat the steps", "as in the previous test case",
     ❌ "select values per the test case name"
     Each step must read independently of other test cases.

3. Expected result:
   — By default — a separate Expected Result after significant steps, not one shared block at the end
   — State the result after steps where:
     • validation occurs
     • UI state changes
     • data is submitted
     • an error/message is displayed, etc.
   — Wording:
     • "The system displays…"
     • "The field is highlighted with an error…"
     • "The button becomes enabled/disabled…", etc.
   — Source of the expected result — requirements/spec, then mockups. The implementation/environment is NOT a source:
     take only exact element names from the implementation; the expected
     BEHAVIOR comes from requirements and mockups. If the implementation
     diverges from the requirements — that is a bug or a question for the analyst, not a basis for the expected result.

4. Coverage:
   Include in coverage:
   — Positive scenarios
   — Negative scenarios
   — Boundary values
   Do not duplicate identical checks without reason.
   — UI states:
     • default
     • hover
     • focus
     • disabled
     • error
     • loading (if applicable), etc.
   — Behavior on:
     • page reload
     • navigation
     • network loss (if there are integrations), etc.
   — Optimize the set thoughtfully, but never at the cost of quality and coverage
   — Run checks at these resolutions (if the task involves UI/responsive layout):
     Desktop: 1920x1080, 1536x864, 2560x1440
     Mobile: 414x896, 360x800, 393x873, 430x926
   — Form reuse:
     • functionality after a successful submit and return
       (a "Submit another" button, etc.)
     • correctness of all fields and lists on repeat fill
   — Sequential validation:
     • error type switching as input changes
       (e.g.: enter digits → clear the input → the error must
       switch from "Letters only" to "Required field")
     • error independence between fields
       (an error in field A does not affect the error text in field B)
   — Exact error texts:
     • state the expected error text in Expected Result,
       not an abstract "an error is displayed"
       If the error text is unknown — state the expected meaning
   — If a field has extra UI elements
     (a "No middle name" button, a toggle, a clear icon) -
     verify their presence/absence and behavior separately

5. Verification against the implementation:
   — When mockups/screenshots exist — verify test cases against them
   — Log discrepancies as bugs or questions
   — If a field is "optional" per requirements
     but the implementation requires input — that is a bug

6. Integrations:
   If there are APIs / external services:
   — Verify:
     • correct parameter submission
     • 4xx / 5xx error handling
     • no UI crashes, etc.
   — Reflect this in the steps and Expected Result

7. Structure:
   — Test case order: High first, then Normal, then Low
   — Within each group, positive scenarios first, then negative
   — Group logically (Display / Validation / Navigation / Negative)
   — Split Desktop and Mobile if there is responsive layout
   — Target browsers — per project requirements; typical minimum:
     Chrome (Desktop + Android), Safari (iOS)
   — For Mobile-only test cases, prefix the name with `[Mobile]`

8. Style:
   — Businesslike, QA style
   — No filler
   — Clear, unambiguous, reproducible

9. Output:
   — Test cases must be ready for TMS import (CSV)
   — If your TMS MCP is connected (e.g. Zephyr Scale MCP with the
     create_test_case tool) — after validating the md file, offer to create
     the test cases directly instead of manual CSV import; CSV remains a fallback
   — No abbreviations or ambiguous wording
   — File names: `{TASK_KEY}_test_cases.md` and `{TASK_KEY}_test_cases.csv`
     (e.g. `PROJ-1234_test_cases.md`). Save to the current working directory.

10. Export for Zephyr Scale
- Generate the CSV in the "Option 1" (Steps) format:
  Columns strictly: Name, Status, Step, Expected Result, Preconditions, Priority, Type
- Row rule:
  1 CSV row = 1 step
  For the first step of a test case, fill Name and Status
  For subsequent steps of the same test case, leave Name and Status empty
- Fill Expected Result for each step (on the same row)
- Encoding: UTF-8
- Delimiter: comma (,)
- Escape all fields with quotes (") as needed (commas/line breaks/quotes)
- Do not use variables/placeholders like {…} in the CSV (write them out as text)

11. Requirements analysis and clarifications

Distinguish two types of questions about ambiguities:

**Critical for generation** — test cases cannot be written correctly without an answer (contradiction between mockup and description, unclear happy path, unknown validation behavior, missing key scenario):
- Ask directly via `AskUserQuestion` BEFORE starting generation
- Group related questions into one call (max 4 questions at a time)
- If clarifications for the task were already covered earlier in this conversation (context gathered from the issue tracker, questions asked) — proceed to generation without repeat questions

**For the analyst** — require business context unavailable to the user in chat (exact error texts from the API, timings, policies, integration specifics):
- Collect them in a separate "Questions for the analyst" list at the end of the reply
- Once the user brings the answers — update the test cases

12. Coverage completeness assessment:
   — At the end, give a brief assessment: what is covered, what is deliberately not covered, and why

13. Direct creation in the TMS via MCP (if connected):
   — **Boundaries.** If the TMS project is shared across teams — all operations
     stay within your team's folder tree; do not modify other teams' roots or
     include them in reports. Record your root folder in the project's `CLAUDE.md`.
   — Before creating, ALWAYS fetch the current folder tree (`get_folders`
     or equivalent) — the structure is live, subfolders get added; do not
     work from a memorized snapshot.
   — Before generating new test cases, check the target folder's existing
     coverage (search test cases by folder): generate only what is missing;
     overlap with an existing test case is a reason to update it,
     not to create a duplicate.
   — Use folder paths VERBATIM as returned by the API: names may contain
     trailing spaces. When creating new folders, avoid special characters
     (quotes, commas) and mixed alphabets in names — they often break
     API search.
   — Pick the folder by the feature's functionality; for a new feature without
     its own subfolder — offer to create one or ask the user.
   — Content rules are the same as for CSV: 1 step = 1 description,
     expectedResult after significant steps (rules above); word expected
     results as "The system displays…".
   — Link test cases to the issue tracker ticket (issue_links or equivalent) — always,
     if the TMS supports it.
   — Note that the TMS may override the status on creation (e.g. always
     "Draft"); move to "Approved" after review and analyst answers, via update.
   — The md file with the test cases remains a mandatory validation stage BEFORE
     creation in the TMS; CSV (section 10) is the fallback if MCP is unavailable.
   — Runs for the task (on user request): create a test run → set statuses
     as the run progresses (Pass/Fail/Blocked). Accompany a Fail status with a comment
     stating the cause/a link to the defect.
   — **Entry point — the first step of a test case opens the page under test**
     ("Open the page at URL …"), so it is clear where to verify. For test cases
     with a special precondition (success screen, pre-filled form), put the URL
     in the precondition.
   — If the TMS renders descriptions as HTML (e.g. Zephyr Scale DC) — format
     the URL as a clickable link `<a href="https://...">https://...</a>`,
     so the link in the test case is clickable.
