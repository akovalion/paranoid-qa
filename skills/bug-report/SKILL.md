---
name: bug-report
description: Quick bug report in Jira. Invoke via /bug-report. Gathers data, shows a preview, creates the defect in Jira after confirmation.
allowed-tools:
  - AskUserQuestion
  - mcp__atlassian__jira_create_issue
  - mcp__atlassian__jira_update_issue
  - mcp__atlassian__jira_search_fields
  - mcp__atlassian__jira_get_field_options
  - mcp__atlassian__jira_get_issue
---

You help file a bug in Jira quickly. Follow this algorithm:

## 0. Project configuration (fill in for your Jira)

The values below are an example; adapt them to your instance (right here or in the project's `CLAUDE.md`):

- **Default project:** `PROJ`
- **Issue type for a defect:** `Bug` (check the exact type name in your project - in localized instances the type may be named differently, e.g. "Defect"/«Дефект» in Russian ones)
- **Priority values:** as in your Jira (e.g. Highest / High / Medium / Low - or localized)
- **Required custom fields:** in many projects, issue creation fails without them. Example format:
  - `customfield_XXXXX` (Team): `"..."`
  - `customfield_XXXXX` (Detection environment): `{"value": "Test"}`; for a bug found in production - `{"value": "Prod"}`
  Find your fields and their allowed values via `jira_search_fields` and `jira_get_field_options`, or inspect the filled fields of a colleague's recent defect via `jira_get_issue`.

## 1. Data gathering

If the user passed the bug description in the arguments - use it.
If not - ask questions via AskUserQuestion:

Required data:
- What happened (actual result)
- What was expected (expected result)
- Steps to reproduce
- Environment (environment name, browser, device)

Optional:
- Project (default - from the configuration)
- Priority (default medium)
- Assignee

## 2. Ticket format

Type and priority - per the configuration (section 0).

Summary: a brief description of the problem, no [BUG] prefixes or similar.

Description structure - plain text with bold headers:

```
**Steps to reproduce:**

1. Step 1
2. Step 2

**Actual result:**

Description of what happens.

**Expected result:**

Description of what should happen.

**Environment:**

Environment/browser/device.
```

If preconditions are needed - add a **Preconditions:** block before the steps.
If there is useful context - add an **Additional info:** block at the end.

## 3. Text rules

- Do not use markdown headings (##), only **bold** - Jira does not render the description as markdown; check the rendering on your instance
- Do not use tables in the description
- Language - whatever is standard in your issue tracker
- Write browser names the user-facing way: Chrome (not Chromium), Safari (not WebKit). This also applies to the test engine (run in Chromium → write "Chrome", in WebKit → "Safari")
- Do not link the created bug to other tickets automatically - only on explicit user request

## 4. Preview before creation

ALWAYS show the user the full ticket text and wait for confirmation before calling mcp__atlassian__jira_create_issue. Preview format:

```
**Type:** Bug
**Priority:** Medium
**Assignee:** (if specified)
**Project:** PROJ

**Summary:** ...

**Description:**
(full description text)
```

Only after explicit confirmation ("yes", "ok", "create it") - call the creation API.

## 5. After creation

Output the key and link of the created ticket. If the assignee was not set - warn the user.

**Screenshots:** if the session has bug screenshots (file paths) - after creation, attach them via `mcp__atlassian__jira_update_issue` (the `attachments` parameter, comma-separated paths). The screenshot must be targeted (the problem element up close), not a fullPage shot of the whole page. If no suitable screenshot exists - suggest the user take one and attach it.
