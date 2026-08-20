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

0. Source completeness and honest limitations:
   — Before generating, collect ALL sources and track their status explicitly. In the
     final report include a source table: ticket / ticket attachments / linked issues /
     wiki (Confluence) / Figma node dump / visual review of ALL frames / Figma comments /
     implementation (if any) — for each: studied | not studied | what blocked it.
     "Not studied" with no reason and no workaround plan is an unacceptable report state.
   — Hit a tool limitation (truncated MCP response, unreachable file, crashed subagent)?
     Do NOT degrade silently: tell the user immediately and propose a workaround.
     Typical example: tracker MCP truncates ticket attachments by response size — the
     same files often live on linked wiki pages, where a tool that saves the file to
     disk in full can fetch them (for Confluence — `confluence_download_attachment`).
   — A subagent's self-report ("read everything, no gaps") is not evidence: spot-check
     the facts your expected results are built on (texts, field sets, labels, NUMBERS — sizes, spacing, gap) against
     the primary source (frame visual, file, live system).
   — Figma comments are not available via MCP (`get_figma_data` does not return them):
     BEFORE generating test cases, explicitly ask the user for the mockup comments
     (as text or screenshots) — they often carry corrections on top of the mockup
     (error texts, removed fields, final wording). Until you have them, that source
     stays open, and the report says so.

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
   — FORBIDDEN in test cases: wording like "capture on the first run", "clarify
     against the implementation", "verify with the implementation" — it turns
     testing into documenting whatever was built. An unknown text/behavior is a
     question for the analyst BEFORE the run (section 11); the expected result
     states the observable expected meaning. The only exception is taking a
     reference from a working PROD implementation of the same requirement (e.g.
     the same validation text on a live form), when the analyst has explicitly
     confirmed the requirement is unchanged.

4. Coverage:
   **Negatives are a required artifact, not optional.** Add a dedicated "Negative/Boundary" group; in the coverage assessment (section 12) list which negative classes are covered and which are consciously skipped (with a reason). A positive-only set is incomplete, even if the object looks simple/navigational.
   **Overlays/modals/panels (an example pack for one object type):** scroll lock (position preserved, background not scrollable, scrollbar-width compensation with no "jump"), close via ×/Esc/backdrop click/Back, deep-link and reload (state in URL), double-click/spam, resize while open, overlay stacking, **fits the viewport at EVERY breakpoint (incl. tablet and short/landscape screens): content not clipped vertically OR horizontally (nothing runs off the edges), internal scroll when content is taller than the viewport, every element and button (submit/footer/close) reachable, safe padding from edges**. Other object types have their own negative pack (forms, lists, navigation, APIs; see references).
   **Repeating blocks and dynamic collections (add/remove N participants, items, addresses, files) — dedicated test cases, not a line inside the submit case.** A classic design gap: people write "Add an element", "Remove an element", "Limit" and "Submit with elements added" — coverage looks complete while the essential thing goes unchecked: WHAT IS ACTUALLY SENT IN THE REQUEST for each count. Plan at least three cases:
   • **Request composition for every count** — 0, 1, 2, … maximum; the expected result states the number of array elements AND the full composition, not "the application was submitted". Intermediate counts are mandatory: array-assembly bugs surface at 2-3 elements, not at the boundaries.
   • **Request composition after a deletion before submit** — delete from the start, from the middle and from the end; the middle is critical (index-based `key` makes block data drift). Expected result: exactly the remaining set is sent, with no shift.
   • **Validation inside a block** — required fields, allowed characters, formats and boundaries verified on an added block, not only on the form's primary fields; separately record how the block's rules DIFFER from the main form (e.g. the age limit does not apply to a participant).
   Test data for such cases uses **unique values in every block** (Alpha/Beta/Gamma, dates with distinguishable day and month: 11.01, 22.02). Identical data hides swapping and off-by-one shifts, and 01.01 masks a day/month transposition during ISO conversion.
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
     Tablet: 768x1024, 1024x768
   — **Layout integrity at EVERY breakpoint — for ANY object, not just modals:** nothing clipped vertically or horizontally or running off the edges; every element, text, icon and button visible and reachable; scroll when content exceeds the viewport (internal scroll for overlays); composition and placement verified against the mockup for THAT specific breakpoint (no item should disappear, move, or flip its icon side). Modals/overlays are just one instance.
   — **Verify alignment geometrically, not by eye:** for "centered" — the element's center matches the container/viewport center (tolerance ~1-2px); for left/right — the edge offsets; for symmetry — equal paired margins. Presence ≠ correct position. At extreme widths (2560+ and the project's minimum supported mobile width, usually 360) check both overflow AND centering/alignment — that's where the layout math most often breaks (fixed left, max-width container, grid, absolute).
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

5. Verification against the implementation and mockups:
   — When mockups/screenshots exist — verify test cases against them
   — Figma — ALWAYS look at the mockup with your own eyes, not only its structure:
     the node dump (`get_figma_data`) gives the grid and layout as text, but part of
     the content is hidden in component templates (`template=…`) and never reaches the
     dump; breakpoint differences (desktop/mobile) are invisible in the tree. Also
     download and view ALL frames of the object — every screen/state, desktop AND
     mobile (`download_figma_images`). Sampling "key" frames is forbidden: mismatches
     live precisely in the unviewed ones (filled states, mobile variants, modals).
     Only the visual gives exact button/card labels, the full contents of groups, and
     catches breakpoint mismatches; never derive alignment/button widths from the text
     dump — only from the image. NEVER derive NUMERIC SIZES (block heights, spacing,
     gap) from the dump at all: inside a wrapper frame sits a raster with ITS OWN
     `dimensions` — often wider and taller than the container, `absolute`, offset and
     clipped by it; that is the size of the IMAGE, not of the block. Containers with
     `sizing: hug` do not expose their real height in the dump at all. Verify sizes
     from the PNG export plus arithmetic: card height = image + gap + caption lines;
     strip width = sum of cards + gap×(n−1) — the same check proves the gap itself. Log the viewed frames in the source table (section 0);
     mockup demo data that contradicts its own validation (Cyrillic in a "Latin only"
     field) goes to the analyst questions
   - **When RUNNING test cases against the implementation the same rule applies as for
     the mockup: LOOK WITH YOUR EYES.** DOM, `innerText`, the accessibility snapshot and
     computed styles give structure, text and behavior, but are blind to appearance -
     that is how you miss the wrong component variant (a grey button instead of white
     with a border), broken spacing, fonts, radii, swapped illustrations. For every
     state you verify, take a screenshot of the implementation and open it next to the
     mockup frame; run hover/focus/active separately - they do not exist in the DOM.
     A screenshot that failed to save blocks the step. Reporting "verified" without
     having looked at a single screenshot of the implementation is not acceptable
   — By default write expected results 1:1 with the mockup (exact headings, texts,
     full list/group contents, names, icons) — max precision is the default. Relax the
     content match ONLY when the user explicitly says not to tie to content (e.g. the
     test environment's content differs from the mockup): then verify the block's
     presence and key names/headings/icons without hardcoding a rigid full list.
     Structure, headings and key names are always verified exactly
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

14. Parallel execution via subagents (pays off from ~10 test cases up):

   **Delegate — mechanical work where the text already exists:**
   — **Reading large exports.** When a design or API export does not fit into the tool
     response and lands in a file, do not grep it selectively: you will miss whole frames.
     One subagent per node, with an explicit task — "read the file IN FULL in ~160-line
     chunks via offset/limit; return the complete list of items with VERBATIM texts,
     sizes, spacings, component states and designer annotations". Run all nodes in parallel.
   — **Uploading test cases to the TMS** from the approved md file: 6-8 test cases
     per subagent, about 4 subagents at once.
   — **Bulk status changes** (Draft → Approved after review) and **filling in run
     results**: split the list of keys between subagents.
   — **Bulk text edits of test cases that already exist** (typos, reworded expected
     results after the analyst answers): split the list of keys between 3-4 subagents.

   **Do not delegate — here an error costs more than the speed gains:**
   — the wording of names, steps and expected results: one voice and precision
     matter more than speed;
   — the folder choice, the decision to create a section, the list of questions
     for the analyst;
   — the final verification.

   **Uploader subagent prompt — the mandatory minimum:**
   — a verbatim call template with the project key, folder path (copied character for
     character from the folder API), custom fields, issue links and priority already
     filled in;
   — **"insert an HTML link as a real `<a href="...">...</a>` tag, do NOT escape it
     into `&lt;a&gt;`"** — otherwise the TMS shows the tag as plain text;
   — "do not rewrite, shorten or improve the test case text — transfer it verbatim
     from the md file";
   — "if a create call returns an error or an unclear result, do NOT retry it
     (duplicate risk) — report the key back instead";
   — return the list of created keys in test case order.

   **Editor subagent prompt (editing test cases that already exist) — the mandatory minimum:**
   — the exact list of keys for that subagent and a ban on opening any other key: a key
     range routinely contains test cases owned by other teams;
   — **"sort the steps returned by the fetch call by their `index` before sending them
     back"** — the API returns them in arbitrary order, and without sorting the scenario
     comes out shuffled;
   — **"the update call replaces the whole test script"** — carry over EVERY step
     verbatim, changing only the agreed substrings;
   — pass name / objective / precondition only if the edit actually touched them; do not
     pass priority, status, folder, issue links or custom fields — the fields you omit
     stay as they were;
   — "insert an HTML link as a real `<a href="...">...</a>` tag, do NOT escape it";
   — "no match inside the test case — do not call update at all";
   — "on an error or an unclear result do NOT retry the call";
   — return one line per key: changed (which fields and steps) | unchanged | ERROR.

   **Verification after the upload is mandatory and is done by you, not by the subagent:**
   search test cases by folder (count, priorities, type) plus fetch 1-2 test cases in
   full (link rendered as a tag, steps in place, issue links set). A subagent's
   "everything created" report is not evidence.

   **After a bulk edit the verification is yours as well, and it covers every case:**
   fetch EVERY edited test case — the new wording is in place, the old one is gone, step
   indexes run 0..N in scenario order, links are still tags, issue links and type are
   not reset.
