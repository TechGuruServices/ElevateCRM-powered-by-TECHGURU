<!--
  ElevateCRM + Inventory · Modern README
  Assets needed:
  - assets/logo.png   (transparent background preferred)
-->

<p align="center">
  <picture>
    <source srcset="assets/logo.webp" type="image/webp">
    <img src="assets/logo.png" alt="ElevateCRM Logo" width="240">
  </picture>
</p>

<h1 align="center">Elevate Your Business Management</h1>
<p align="center">
  <strong style="font-size:1.2em;">Streamline. Automate. Elevate.</strong><br/>
  Next-generation CRM & Inventory platform designed for small and medium businesses that hate clunky software.
</p>

<p align="center">
  <a href="#-overview">Overview</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-tech-stack">Tech Stack</a> ·
  <a href="#-quickstart">Quickstart</a> ·
  <a href="#-desktop-app">Desktop</a> ·
  <a href="#-screenshots">Screenshots</a>
</p>

---

## ✨ Overview
ElevateCRM brings together **customer management**, **inventory tracking**, and **process automation** in one clean, modular system.  
It’s opinionated where it helps, flexible where it counts, and fast enough to stay out of your way.

---

## 🚀 Features
- **CRM** — Pipelines, notes, tasks, and activity timelines  
- **Inventory** — Real-time stock, purchase orders, barcode/QR scanning  
- **Automation** — Background jobs and workflows powered by Celery + Redis  
- **Analytics** — KPIs, dashboards, and exports for smarter decisions  
- **Cross-platform** — Works as a web app, desktop (Electron), and mobile-friendly PWA

---

## 🛠 Tech Stack
| Layer        | Tools |
|--------------|-------|
| **Frontend** | Next.js 14 · TypeScript · Tailwind CSS · shadcn/ui |
| **Backend**  | FastAPI · SQLAlchemy 2.x · Pydantic |
| **Database** | PostgreSQL (production) · SQLite (development) |
| **Infra**    | Redis · Celery for background tasks |
| **DevOps**   | Docker Compose · Alembic migrations |
| **Desktop**  | Electron (Win/macOS/Linux) |

---

## ⚡ Quickstart

### Option A — Docker (fastest)
Prereqs: Docker Desktop 4.4+ with Compose v2

```bash
# Clone
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Run everything
docker compose up -d --build

# Access
# Frontend → http://localhost:3000
# API Docs → http://localhost:8000/docs
