# Session stats collector (opt-in)

Measure your own agent instead of guessing. Claude Code writes a transcript of
every session to `~/.claude/projects/` - this script turns those logs into
numbers: how many hours the agent actually worked, how many hours you were
present next to it, and which lines of its replies look like defect findings.

```bash
python3 collect.py 2026-08-01
```

Output per work session:

```
===== a1b2c3d4 | 2026-08-02 | agent ~2.8h | human ~2.2h | tools: {'playwright': 203}
  first message: https://tracker/TASK-123 test this on staging
  candidate: ...active tab is cut off on the left - defect of the component...
```

## Method - and its honest limits

- **Agent hours = active time.** Sum of gaps between session events with pauses
  over 30 min cut out. Never use wall-clock: a session left open for a week
  reports 170 fake hours.
- **Human hours = presence.** Same math over your own messages, 20-min cap.
  This is a lower bound - silent watching leaves no log lines.
- **Defect candidates are hints, not counts.** The script surfaces lines to
  read; confirming what is a real finding, who found it, and what turned out
  false stays a human judgement.
- **Transcripts rotate** (30 days by default). Archive the raw `.jsonl` files
  if the dataset should outlive the rotation.

## Adapting

Edit the config block at the top: add your project folder fragments to
`WORK_DIRS` (a project folder is work by definition - automation sessions make
few MCP calls), sandboxes to `SKIP_DIRS`, and tune the MCP families in
`WORK_TOOLS` for home-folder sessions.

Privacy: the script only reads local files and prints to stdout. Nothing
leaves your machine.
