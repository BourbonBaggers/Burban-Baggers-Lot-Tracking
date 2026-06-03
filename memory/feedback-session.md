# Feedback Session

## User Preferences

- The user is trying Codex after using Claude and wants continuity with Claude-style project
  files and memory.
- The user wants frequent Git commits at major checkpoints so work can resume cleanly if a
  session runs out of tokens.
- The first commit may be documentation only.
- GitHub repository name: `Burban Baggers Lot Tracking`.
- GitHub visibility: public.
- The user grants intent-level permission to run local bash commands and add or delete files
  within this repository only. The Codex environment may still require approval prompts.
- Use SSH for deployment when needed: `jayk1@192.168.0.124`.
- User observed that batch creation appeared to hang for about 10 seconds after lot number
  generation. Root cause was the single sync Gunicorn worker blocking behind an idle local
  connection; the app now uses 2 workers and 4 threads.
- User supplied the Toasted Cherry Simple Syrup UPC PNG and clarified it should be product
  configuration, not something uploaded on every lot. Labels should maximize barcode size
  and include expiration date plus lot number. Toasted Cherry shelf life starts at 12 months.

## UX Preferences

- Internal tool, not customer-facing.
- Optimize for speed of data entry.
- Desktop-first, tablet-friendly.
- Favor forms and tables over fancy dashboards.
- Minimize clicks.
- Every major screen should be printable.
- No unnecessary JavaScript frameworks unless clearly beneficial.
