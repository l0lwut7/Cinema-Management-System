# Contributing to the Cinema Management System

This document defines how to run the project locally and how to contribute with minimal merge conflicts.

## Core Rules
1. Never commit directly to `main`.
2. Every issue must be developed on its own branch.
3. Open a Pull Request (PR) for review before merge.

## First-Time Setup

### 1. Clone the repository
```bash
git clone <repo-url>
cd Cinema-Management-System
```

### 2. Create virtual environment and install dependencies
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Flask app
```bash
python run.py
```

Check routes:
- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/styleguide`
- `http://127.0.0.1:5000/components`

### 4. Optional database setup
Run these in your MySQL client when working on SQL tasks:
- `database/cinema.sql`
- `database/seed.sql`
- `database/queries.sql` (for checks/examples)

## Daily Contribution Workflow

### 1. Claim an issue
Comment on the issue and assign yourself.

### 2. Sync local `main`
```bash
git checkout main
git pull origin main
```

### 3. Create a branch from `main`
Use one branch per issue:
- `feature/<short-topic>`
- `bugfix/<short-topic>`
- `docs/<short-topic>`
- `refactor/<short-topic>`

Examples:
- `feature/styleguide-buttons`
- `bugfix/session-timeout`
- `docs/run-instructions`

### 4. Commit with focused scope
Keep commits small and issue-focused.

Good commit examples:
- `docs: add flask quick start`
- `templates: add card component variants`
- `styleguide: normalize spacing tokens`

### 5. Open PR early
Open as draft if needed, then request review when ready.

## Template and Blueprint Structure Policy (Conflict Prevention)

To reduce merge conflicts, each issue should map to a single feature area and avoid touching shared files unless required.

### Preferred ownership model
1. Blueprint scope:
Each feature should have its own blueprint module. Keep feature routes in that module instead of putting everything in one shared file.

Suggested target structure as the project grows:
```text
app/
|- blueprints/
|  |- bookings/
|  |  |- __init__.py
|  |  |- routes.py
|  |- movies/
|  |  |- __init__.py
|  |  |- routes.py
|- templates/
   |- bookings/
   |- movies/
   |- shared/
```

2. Template scope:
Put issue-specific templates inside a feature folder:
- `app/templates/bookings/...`
- `app/templates/movies/...`

Shared template fragments go under:
- `app/templates/shared/...`

### File touch rules
1. Do not edit `app/templates/base.html` unless the issue explicitly requires a global layout change.
2. Do not bundle unrelated styleguide/component changes in the same PR.
3. If a change affects shared files, mention it explicitly in PR description under `Shared files changed`.
4. If two open issues would modify the same shared file, coordinate and split work before coding.

### PR checklist for structure safety
- Branch created from latest `main`
- Issue scope is respected (no unrelated files)
- Feature files are under the correct blueprint/template folder
- Shared file edits are justified in PR description
- App runs locally (`python run.py`) and relevant pages are manually checked

## Review Expectations
1. At least one approval before merge.
2. Resolve all review comments.
3. Rebase or update branch if it falls behind `main`.

## Quick Commands
```bash
# create branch
git checkout -b feature/<topic>

# stage and commit
git add .
git commit -m "<type>: <short message>"

# push branch
git push -u origin feature/<topic>
```
