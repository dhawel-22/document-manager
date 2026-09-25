# Document Manager: Opening Document

**Version:** 1.3 · **Approved by:** Ernie, 2026-09-24 · **Owner:** Ernie
**Drafted by:** Claude, from thread "00 · Planning talk"
**Changes:** v1.1 (2026-09-25): D-009 answered: public. Made through a pull request.
v1.2 (2026-09-25): D-016 and D-017 added, from the guards plan. Made through a pull request.
v1.3 (2026-09-25): D-018 added. Made through a pull request.

Status labels (per D-015):
- **Ernie:** decided by Ernie
- **On trust:** Claude's recommendation, accepted on trust, to be proven in Phase 0
- **Waiting:** needs Ernie's answer

## 1. Why this project exists
AI can write code in minutes, but projects get contaminated by silent edits,
made-up rules and false "done" reports, and checking the work then takes
weeks. This project builds the protection first (the vault), then uses it to
build a tool worth having.

## 2. Goal (Ernie)
- Product: a robust document manager with a Python GUI.
- Long term: manage all of Ernie's files, across network shares and Google Drive.

## 3. Working rules
1. Documentation first. No actions of any kind, not even read-only checks,
   until the relevant document is approved and Ernie says "go." (Ernie)
2. Claude proposes; only Ernie decides. How decisions are recorded follows D-015. (Ernie)
3. One change at a time: test, check in, stop. (Ernie)
4. Never claim "done" or "verified" without running the check (Ernie).
   Show evidence: change ID, real test output, file locations (On trust).
5. Say "I haven't found it" or "I couldn't verify it." Never fill a gap with
   something plausible. (Ernie)
6. Missing information stays "unavailable," never guessed; for example,
   publication dates. (Ernie)
7. If it's only in a chat, it doesn't exist. (On trust)

## 4. Decisions

| ID | Decision | Status |
|---|---|---|
| D-001 | No new project work until the vault is built and tested | Ernie |
| D-002 | First goal: a practice week to set up the tools, practice with examples and validate | Ernie |
| D-003 | Small pieces chained together; no 1,000-line files. The glue is fixed code, never AI improvising | Ernie; glue detail On trust |
| D-004 | Project split into spec, decisions, tests, code, manual, docs. Each area has its own lock level | Ernie; lock levels On trust |
| D-005 | Separate, titled threads in a sidebar group, linked by a thread log | Ernie; thread log On trust |
| D-006 | Each tool gets its own thread | Replaced by D-013 |
| D-007 | Teaching aids in every section. Every lesson example actually runs | Ernie; "actually runs" On trust |
| D-008 | Decision records for every section: one register, replaced but never edited | Ernie; register rules On trust |
| D-009 | Practice repository on GitHub Free, public; GitHub Pro when private work starts; no real data in any repository | Ernie: public; rest On trust |
| D-010 | Practice project is a document register | Replaced by D-011 |
| D-011 | The project is a document manager with a Python GUI; long term, all network files and Google Drive. Engine first, thin GUI | Ernie; engine-first and thin GUI On trust |
| D-012 | SQL added to the required tools | Ernie; tool choices On trust |
| D-013 | One project, the Document Manager. The vault is Phase 0. Small sidebar; threads added only when needed | Ernie |
| D-014 | Code lives at D:\python\projects\document-manager, not in Google Drive | Ernie |
| D-015 | Ernie decides goals, priorities, money, risk and what "correct" means. Technical choices are recorded "On trust" and proven by evidence. Plain-language questions. Optional second opinion from the OpenAI side | Ernie |
| D-016 | Claude asks before every file change and every command that changes something; look-only commands run without a click | Ernie |
| D-017 | The Claude Code guards live in a settings file that Windows protects; changing it needs Ernie's administrator approval | Ernie |
| D-018 | AI work is credited by the AI account plus a plain note naming the model, like "Made with Claude Opus 5.5"; no co-author lines that list outside accounts | Ernie |

## 5. Phases (On trust)
Each phase must pass a clean scorecard before the next one starts.
- Phase 0, vault and engine (practice week): set up the tools; build the engine
  (register, fingerprint, verify, report) on fake documents; fire drills; scorecard.
- Phase 1: the GUI (kept thin, all logic in the engine); manage the project's
  own documents.
- Phase 2: one real network folder and one Google Drive folder, read-only.
- Phase 3: all network files, read-only.
- Later: anything that moves, renames or deletes files, behind backups and its
  own fire drills.

## 6. How work happens (On trust)
- Talk mode: discuss freely. Nothing changes.
- Work mode: GitHub issue (task template) → plan and check-out → branch →
  small change with local tests → pull request → GitHub checks →
  independent review → Ernie approves and merges → wrap-up
  (thread log, decisions, lessons).

## 7. Project layout (On trust)
spec/  decisions/  tests/  src/  docs/manual/  docs/technical/  docs/teaching/
vault/  CLAUDE.md  AGENTS.md
The spec is the source of truth. Changes flow spec → tests → code → docs,
linked by rule IDs.

## 8. Tools (On trust, except SQL: Ernie)
- Vault: Git, GitHub (plus the AI's own account), GitHub Actions
- Guards: Claude Code permissions, hooks, rewind, plan mode
- Testing: pytest, answer-key comparison, Pydantic/pandera, pre-commit
- Database: SQLite, DB Browser for SQLite, versioned schema scripts
- Review and glue: independent review agents, workflows, worktrees
- Our scripts: check-out/check-in, tamper check
- GUI: PySide6 or Tkinter, decided in Phase 1
- Cost: GitHub Pro (about $4 a month) once private work starts; everything else free

## 9. Open questions (Waiting)
1. Answered 2026-09-24: yes, public. Is it okay if anyone on the internet can
   see the practice project (code and fake documents only)? Yes: free, with the
   full lock. No: $4 a month, or no lock until the fire drills. (D-009)
2. Who are the lessons for?
3. Do you have Microsoft 365 / SharePoint?
4. Google Drive: mostly uploaded files, or native Docs and Sheets?
5. Roughly how many files across the network?
6. Export read-only copies to G:\My Drive\Document Manager?

## 10. First steps after "go" (On trust)
One step at a time. At each stop, Ernie reviews before anything continues.

Local:
1. Check what's installed: git, Python, GitHub's command-line tool (read-only).
2. Create D:\python\projects\document-manager.
3. Start git in that folder.
4. Save this document as docs/00-opening-document.md and make commit #1.
→ Stop: Ernie reviews commit #1.

GitHub (Ernie does the account steps; Claude guides):
5. Ernie confirms their own GitHub account and creates the AI's account
   (separate email address).
6. Ernie creates the repository (visibility per D-009), and commit #1 is sent up to it.
7. Add the AI's account as a helper, switch on the branch lock, then test it:
   a push straight to main must be refused.
→ Stop: Ernie reviews. Next comes the plan for the Claude Code guards,
  written and approved before it's built.
