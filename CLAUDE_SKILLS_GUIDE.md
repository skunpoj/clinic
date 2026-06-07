# Using Custom Skills on Claude Code Web via Mobile App

A step-by-step guide to building, deploying, and activating custom slash commands in Claude Code web sessions from the Claude mobile app.

---

## What Are Claude Skills?

A **Claude Skill** is a custom slash command (e.g. `/make-pptx`, `/clinical-query`) that tells Claude exactly what to do when invoked. Skills are defined by a `SKILL.md` file stored in your GitHub repository. Claude Code reads the `.claude/` folder on session startup and automatically registers every skill it finds.

**Key properties:**
- Defined entirely in Markdown — no server, plugin install, or API registration needed
- Version-controlled alongside your code
- Available across Claude Code web, mobile, and IDE extensions
- One `SKILL.md` per skill; folder name becomes the slash command name

---

## Prerequisites

| Requirement | Details |
|---|---|
| GitHub repository | Public or private; you need push access to the branch the session uses |
| Claude mobile app | Latest version (iOS or Android); signed in to your Anthropic account |
| Claude Code session | Repository connected; Claude Code re-reads `.claude/` on every new session start |

---

## Step 1 — Create the Folder Structure

Skills live in `.claude/skills/<skill-name>/` at the root of your repository. The folder name becomes the slash command name.

```
your-repo/
└── .claude/
    └── skills/
        ├── make-pptx/
        │   ├── SKILL.md        ← required
        │   └── pptxgenjs.md    ← optional supporting guide
        └── clinical-query/
            └── SKILL.md        ← required
```

Create the directory:
```bash
mkdir -p .claude/skills/your-skill-name/
```

---

## Step 2 — Write SKILL.md

`SKILL.md` is the complete definition of your skill. The `# /your-skill-name` heading must match the folder name.

**Minimal template:**
```markdown
# /your-skill-name

One-line description of what this skill does.

## Usage
/your-skill-name [optional args]

## What this skill does
1. Step one
2. Step two
3. Step three

## Instructions
When the user invokes this skill:
- Do X using `bash command`
- Then do Y
- Finally deliver Z to the user

## Output format
Describe the expected output structure here.
```

**Tips for effective SKILL.md files:**
- The **Instructions** section is what Claude actually follows — be concrete.
- Name specific files, commands, and expected outputs.
- Reference other `.md` files in the same folder for long supporting guides.
- Keep the trigger description short — it appears in autocomplete.

---

## Step 3 — Commit & Push to GitHub

```bash
# Stage the skill files
git add .claude/skills/your-skill-name/

# Commit
git commit -m "Add /your-skill-name custom skill"

# Push to the branch your session uses
git push origin main
```

> **Important:** Skills must be on the branch that your Claude Code session is pointed at. Skills on a feature branch only activate in sessions using that branch. Merge to `main` for universal access.

---

## Step 4 — Open Claude Code on Mobile App

1. Open the **Claude mobile app**
2. Tap the **Code** tab at the bottom of the screen
3. Tap **New session** (or open an existing session linked to your repo)
4. If starting fresh, tap **Connect repository** → select your repo
5. Claude clones the repo and scans `.claude/` on startup — skills are registered automatically

> Each new session re-reads the repository. If you pushed skills after a session started, **start a new session** to pick them up.

---

## Step 5 — Activate & Use Your Skill

In the chat input, type `/` to see registered skills in the autocomplete list. Select your skill or type the full command:

```
/your-skill-name
/clinical-query diabetic patient with kidney complications
/make-pptx
```

Claude reads `SKILL.md` and executes the instructions exactly as written.

---

## Skills Built in This Project

### `/clinical-query`

Runs semantic retrieval against the clinical note corpus.

**File:** `.claude/skills/clinical-query/SKILL.md`

**What it does:**
1. Runs `scripts/demo.py --sample --query "<your query>" --top-k 5`
2. Displays a ranked markdown table (Rank / Score / Specialty / Description)
3. Generates a clinical summary (Claude API or rule-based fallback)
4. Reports retrieval quality — score spread and rank-1 confidence

**Usage:**
```
/clinical-query diabetic patient with kidney complications
/clinical-query COPD with oxygen desaturation
/clinical-query acute chest pain ST elevation
```

---

### `/make-pptx`

Regenerates the Clinical Note Retrieval System presentation.

**File:** `.claude/skills/make-pptx/SKILL.md`  
**Supporting guide:** `.claude/skills/make-pptx/pptxgenjs.md`

**What it does:**
1. Runs `python3 scripts/make_pptx.py`
2. Runs content QA with `markitdown`
3. Delivers `Clinical_Note_Retrieval_System.pptx` to the user
4. Commits and pushes the updated file

**Based on:** Official [anthropics/skills PPTX skill](https://github.com/anthropics/skills/blob/main/skills/pptx/SKILL.md), including:
- Full design principles (10 colour palettes, typography guide, layout options)
- Required QA workflow (content QA + visual QA with subagents)
- Converting slides to images for visual inspection
- Common mistakes to avoid

**Usage:**
```
/make-pptx
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Skill not showing in `/` autocomplete | Skills are on wrong branch — merge to `main` |
| Skill doesn't appear after pushing | Start a **new session** — existing sessions don't reload `.claude/` |
| Command name doesn't match folder | Folder name must exactly match the `# /heading` in `SKILL.md` |
| Claude ignores the instructions | Be more specific in the Instructions section — name files and commands |
| Skill triggers but does the wrong thing | Add an explicit Output format section to constrain Claude's response |

---

## Best Practices

- **One skill per folder, one `SKILL.md` per skill** — keep them focused
- **Name the folder exactly what you want after `/`** — no spaces, use hyphens
- **Keep Instructions concrete** — name files, bash commands, and expected outputs
- **Store supporting guides in the same folder** — Claude can read them via relative links
- **Version-control skills alongside the code they automate** — they evolve together
- **Test by starting a fresh session** after every push — this mirrors how users will experience them

---

## File Locations in This Repo

```
clinic/
├── .claude/
│   └── skills/
│       ├── clinical-query/
│       │   └── SKILL.md
│       └── make-pptx/
│           ├── SKILL.md
│           └── pptxgenjs.md
├── CLINICAL_EXAM.md          ← exam submission write-up
├── CLAUDE_SKILLS_GUIDE.md    ← this file
├── Clinical_Note_Retrieval_Exam.pptx
├── Claude_Skills_Guide.pptx
└── Clinical_Note_Retrieval_System.pptx
```
