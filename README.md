Casual Copilot mode

You borked the install, so here’s a single, clean, copy-paste README with a fixed, bulletproof install section. Same sleek format, tighter steps, fewer opportunities for chaos.

<!--
  README: ElevateCRM + Inventory
  Modern layout with gradient banner and centered hero.
  Place your logo at: assets/logo-elevatecrm.png (transparent PNG, ~200px wide)
-->

<!-- Slim gradient banner -->
<p align="center">
  <svg width="100%" height="92" viewBox="0 0 1200 92" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ElevateCRM">
    <defs>
      <linearGradient id="elevateA" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1FA3FF"/>
        <stop offset="50%" stop-color="#5B5CFF"/>
        <stop offset="100%" stop-color="#8A2BE2"/>
      </linearGradient>
    </defs>
    <rect width="1200" height="92" fill="url(#elevateA)"/>
  </svg>
</p>

<div align="center">
  <img src="assets/logo-elevatecrm.png" alt="ElevateCRM Logo" width="200" />
  <h1>ElevateCRM + Inventory</h1>
  <p><em>Powered by TechGuru</em></p>
  <p><strong>Streamline. Automate. Elevate.</strong></p>

  <p>
    <a href="#-overview">Overview</a> ·
    <a href="#-features">Features</a> ·
    <a href="#-tech-stack">Tech Stack</a> ·
    <a href="#-quickstart-installation">Installation</a> ·
    <a href="#-screenshots">Screenshots</a>
  </p>
</div>

---

## ✨ Overview
ElevateCRM unifies **customer management, inventory tracking, and automation** in a sleek, modular system.
Opinionated where it helps, flexible where it counts, intolerant of clunky workflows.

---

## 🚀 Features
- **Customer Management** — Pipelines, tasks, notes, activity timelines  
- **Inventory Control** — Real-time stock, POs, barcode/QR capture  
- **Automations** — Workflow engine with Celery + Redis  
- **Analytics** — KPIs and dashboards  
- **Cross-Platform** — Web app, desktop (Electron), mobile-friendly

---

## 🛠 Tech Stack
| Layer        | Tools & Frameworks |
|-------------|---------------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend**  | FastAPI, SQLAlchemy 2.x, Redis, Celery |
| **Database** | PostgreSQL (prod), SQLite (dev) |
| **Desktop**  | Electron (Win/macOS/Linux) |
| **DevOps**   | Docker Compose, Alembic migrations |

---

## ⚡ Quickstart (Installation)

Two ways to run. If you like painless: **Docker**. If you’re a purist: **Manual**.

### Option A — Docker (fastest)
Prereqs: Docker Desktop 4.4+ and Docker Compose v2

```bash
# 1) Clone the repo
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

# 2) Copy example envs (edit values later if needed)
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3) Start everything (API, Web, DB, Redis)
docker compose up -d --build

# 4) Open the app
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs

# 5) Stop when you’re done
docker compose down

Option B — Manual (frontend + backend locally)

Prereqs: Python 3.11+, Node 18+, PostgreSQL 14+ (or SQLite), Redis (for automations)

# 0) Clone
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

Backend (FastAPI)

cd backend

# 1) Setup virtual env (Windows PowerShell example)
python -m venv .venv
. .venv/Scripts/Activate.ps1    # macOS/Linux: source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Env & DB
cp .env.example .env             # configure DB_URL, REDIS_URL, SECRET_KEY
alembic upgrade head             # run migrations

# 4) Run API
uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs

Frontend (Next.js)

cd ../frontend

# 1) Install deps
npm install

# 2) Env
cp .env.example .env.local       # set NEXT_PUBLIC_API_URL to http://localhost:8000

# 3) Run dev
npm run dev
# App: http://localhost:3000

Background workers (optional but recommended)

# from backend/
celery -A worker.app worker -l info
celery -A worker.app beat -l info

Desktop App (Electron)

Build a desktop installer after the web app works.

cd desktop
npm install

# TypeScript builds, then package
npm run build && npm run dist

# Output installers in: desktop/dist/

Common fixes
	•	Port in use: change ports in docker-compose.yml or .env.local.
	•	Missing migrations: run alembic upgrade head.
	•	CORS issues: ensure NEXT_PUBLIC_API_URL matches your backend URL.

⸻

📸 Screenshots

<div align="center">
  <img src="assets/screenshot-dashboard.png" alt="Dashboard Screenshot" width="720"/>
</div>



⸻

🌐 Demo

Coming soon…

⸻


<div align="center">
  <sub>MIT License © 2025 • Crafted by <strong>TechGuru</strong></sub>
</div>
```