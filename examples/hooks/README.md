# Enforcement hooks (opt-in)

Rules and skills convince the agent; hooks make key violations technically impossible. Rules live in the context window and lose weight as a session grows. A hook is your code on a lifecycle event — it runs no matter what the model currently "thinks".

Three ready-made gates for Playwright projects:

| Hook | Event | What it does |
|---|---|---|
| `gate-commit.sh` | PreToolUse (Bash) | `git commit` is denied unless there is a fresh green `test-results/.last-run.json` |
| `track-test-edit.sh` | PostToolUse (Edit\|Write) | editing a `*.spec.ts` raises a dirty flag and injects a run reminder into the agent's context |
| `gate-stop.sh` | Stop | the agent cannot finish the turn while tests are dirty; self-clears after a run; a fuse stops it from blocking more than twice in a row |

## Install (copy, not plugin)

These hooks are **deliberately not part of the plugin** — a commit gate silently enabled on your machine by someone else's package would be hostile. Opt in by copying:

```bash
mkdir -p .claude/hooks
cp examples/hooks/*.sh .claude/hooks/ && chmod +x .claude/hooks/*.sh
# merge examples/hooks/settings.json into your .claude/settings.json
```

Requirements: `jq`, Playwright (it writes `test-results/.last-run.json` on every run by itself).

## Design notes

- **Asymmetry principle.** The commit gate denies when in doubt (a false block costs one `npx playwright test`; a false pass costs an untested commit in history). The stop gate lets through when in doubt (a false block risks an infinite stop loop).
- **The deny reason is an instruction.** The agent reads it and acts on it — put the exact command to run in there, not just "not allowed".
- **Fuse required.** An aggressive Stop hook without a block limit can hang a session in a stop-block cycle when the environment is broken.
- **Hooks check form, not meaning.** A green run does not prove the tests are meaningful — `expect(true).toBe(true)` passes any gate. Meaning is caught by review: see the [`test-review`](../../skills/test-review) skill.

Adapt the file masks (`*.spec.ts`, `tests/`) and the artifact path to your project.
