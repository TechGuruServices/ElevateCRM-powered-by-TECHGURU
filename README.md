<!--
  ElevateCRM + Inventory · Modern README
  Tip: put your logo at assets/logo.webp (or logo.png) around 200–240px wide, transparent background.
-->

<!-- Banner (safe external file recommended) -->
<p align="center">
  <img src="assets/banner.svg" alt="ElevateCRM banner" width="100%"/>
</p>

<!-- Hero with primary logo (the star of the show) -->
<div align="center">
  <picture>
    <source srcset="logo.webp" type="image/webp"/>
    <img src="logo.png" alt="ElevateCRM Logo" width="220"/>
  </picture>

  <h1>ElevateCRM + Inventory</h1>
  <p>
    <strong>Streamline. Automate. Elevate.</strong><br/>
    Next-generation CRM & Inventory platform for teams that hate clunky software.
  </p>

  <p>
    <a href="#-overview">Overview</a> ·
    <a href="#-features">Features</a> ·
    <a href="#-tech-stack">Tech Stack</a> ·
    <a href="#-quickstart">Quickstart</a> ·
    <a href="#-desktop-app">Desktop</a> ·
    <a href="#-screenshots">Screenshots</a>
  </p>
</div>

---

## ✨ Overview
ElevateCRM unifies **customer management**, **inventory tracking**, and **automation** in one clean, modular system.
Opinionated where it helps, flexible where it counts, and fast enough to feel invisible.

---

## 🚀 Features
- **CRM** — Pipelines, notes, tasks, timeline, activity log  
- **Inventory** — Real-time stock, POs, barcode/QR scanning  
- **Automation** — Celery + Redis workers, scheduled jobs  
- **Analytics** — Dashboards, KPIs, exports  
- **Cross-platform** — Web app, Electron desktop builds

---

## 🛠 Tech Stack
| Layer        | Tools |
|-------------|-------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend**  | FastAPI, SQLAlchemy 2.x, Pydantic |
| **Infra**    | PostgreSQL (prod), SQLite (dev), Redis |
| **DevOps**   | Docker Compose, Alembic migrations |
| **Desktop**  | Electron (Win/macOS/Linux) |

---

## ⚡ Quickstart
Two paths: **Docker** for one-command setup, or **Manual** for full control.

### Option A — Docker
Prereqs: Docker Desktop 4.4+ with Compose v2

```bash
# 1) Clone
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

# 2) Env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3) Up
docker compose up -d --build

# 4) Open
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
