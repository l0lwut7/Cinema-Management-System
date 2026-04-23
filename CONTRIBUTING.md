# 🎬 Contributing to the Cinema Management System

Welcome to the team! 🚀  
To keep our codebase clean and safe, we follow a structured workflow using:

- **Feature Branches** → Your personal workspace  
- **Pull Requests (PRs)** → Code review before merging  

---

## 🚨 Golden Rule
> ❗ **NEVER write code directly on the `main` branch!**

---

## 🖥️ Required Tool

👉 Install **GitHub Desktop**

---

# ⚙️ 1. First-Time Setup (Do this once)

## 📥 Step A: Clone the Repository

1. Open GitHub Desktop  
2. File → Clone Repository  
3. Select `cinema-management-system`  
4. Click **Clone**

---

## 🐍 Step B: Setup Python Environment

```bash
python3 -m .venv venv
source .venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🗄️ Step C: Setup Database

Run in your MySQL client:

```
database/cinema.sql
database/seed.sql
```

---

# 🔁 2. Daily Workflow

## 📝 Step 1: Claim an Issue

Go to GitHub Issues and comment:
```
I'll take this!
```

---

## 🌿 Step 2: Create a Branch

1. Switch to `main`
2. Click **Fetch origin**
3. Create a new branch:
   - `feature-login`
   - `bugfix-seats`
   - `refactor-database`
   - `docs-readme`
   - `etc.`
   - Or create a branch from the issue by Development → Create Branch from Issue from the issue page on GitHub.
4. Publish branch

---

## 💻 Step 3: Write Code

Structure:

- `app.py / app/` → Backend  
- `templates/` → HTML  
- `database/` → SQL  

---

## 💾 Step 4: Commit & Push

1. Write commit message:
   - Added login page
   - Fixed seat bug
2. Commit
3. Push

---

## 🔀 Step 5: Pull Request

1. Click **Create Pull Request**
2. Fill template
3. Submit PR

---

# ✅ Done!

🎉 Wait for review and merge.

---

Happy coding 🚀
