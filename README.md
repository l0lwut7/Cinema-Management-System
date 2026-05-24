# Cinema Management & Integrated Booking System

Course: SE2230 - Database Systems  
Institution: Yasar University  
Term: Spring 2026

## Team Members
- Sevval Ahishali
- Reis Yildiz
- Alp Yuksekkaya
- Firdevs Palay

## Project Overview
This project is a centralized relational database solution for managing a multi-location cinema chain. It handles core operations such as movie scheduling, theater allocation, seat-level booking flow, and operational analytics.

The current Flask app is primarily used to render and iterate on UI templates, including the styleguide and reusable components.

## Tech Stack
- Database: MySQL Community Server 8.0
- Backend: Python + Flask 3.1
- Frontend: HTML5, Tailwind CSS (server-side rendered templates)
- Design/Architecture: draw.io, dbdiagram.io

## Repository Structure
```text
.
|- run.py
|- app/
|  |- __init__.py
|  |- templates/
|     |- base.html
|     |- components.html
|     |- styleguide.html
|- database/
|  |- cinema.sql
|  |- queries.sql
|  |- seed.sql
|- docs/
   |- ER_Diagram.md
```

## Quick Start (Styleguide + Flask App)

### 1. Prerequisites
- Python 3.11+ (3.10+ also works)
- pip
- Optional: MySQL 8.0 if you want to run SQL scripts locally

### 2. Clone and enter the project
```bash
git clone <repo-url>
cd Cinema-Management-System
```

### 3. Create and activate virtual environment
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the Flask app
```bash
python run.py
```

The app starts on `http://127.0.0.1:5000`.

Useful routes:
- Home: `http://127.0.0.1:5000/`
- Styleguide: `http://127.0.0.1:5000/styleguide`

## Database Setup (Optional for UI work)
If you only work on templates/styleguide, you do not need the database running.

If your issue touches SQL/schema:
1. Open MySQL client:
   ```bash
   mysql -u <username> -p
   ```
2. Create/select your database.
3. Run scripts in order:
   - `database/cinema.sql`
   - `database/seed.sql`
4. Use `database/queries.sql` for query checks and examples.

## Contributing
Contribution workflow, branch naming, and merge-conflict-safe structure rules are documented in `CONTRIBUTING.md`.

## 📸 App Preview

<table>
  <tr>
    <td><b>Main Screen</b></td>
    <td><b>Now Showing</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/cd269b47-be0a-4948-ba52-1699065f30fc" width="400"></td>
    <td><img src="https://github.com/user-attachments/assets/9ddca7f9-013a-410a-8c80-fb285de847e1" width="400"></td>
  </tr>
</table>

<table>
  <tr>
    <td><b>Theatres</b></td>
    <td><b>Login Page</b></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/87fc9c27-6d3a-4a22-8208-2998884c7b45" width="400"></td>
    <td><img src="https://github.com/user-attachments/assets/2f980b65-13c3-4332-a763-3663b75e087f" width="400"></td>
  </tr>
</table>
