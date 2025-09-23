<!-- Slim gradient banner + centered hero -->
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
    <a href="#-installation">Installation</a> ·
    <a href="#-screenshots">Screenshots</a>
  </p>
</div>

---

## ✨ Overview
ElevateCRM unifies **customer management, inventory tracking, and automation** in a sleek, modular system.

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

## 📦 Installation

```bash
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm