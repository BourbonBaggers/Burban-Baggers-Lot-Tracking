# /init-session

Orient for a new work session on this project.

## Steps

1. **Read context files**
   - Read `CLAUDE.md` — project overview, stack, rules, non-goals
   - Read `CLAUDE.local.md` — deployment target, local port, env var notes

2. **Check local environment**
   - Run `docker ps` to confirm Docker Desktop is running (skip if project doesn't use Docker)
   - Run `find . -name "*.py" -newer .git/index 2>/dev/null | head -10` to surface recently touched files (skip if no git yet)

3. **Check git state** (skip gracefully if no repo initialized yet)
   - `git status` — uncommitted changes?
   - `git log --oneline -5` — what was last worked on?

4. **Scan for open TODOs**
   - `grep -rn "TODO\|FIXME\|HACK" --include="*.py" --include="*.html" --include="*.md" . 2>/dev/null | grep -v ".claude"`
   - List any hits so nothing is forgotten

5. **Summarize and ask**
   - In 3–5 bullet points: current state of the project, what's built, what's not, any open issues found above
   - End with: "What are we working on today?"

## Rules
- Be brief — this is orientation, not a report
- If git isn't initialized yet, skip git steps silently
- If Docker isn't running, flag it — builds will fail
- Never summarize what this command itself did; just report state and ask the question
