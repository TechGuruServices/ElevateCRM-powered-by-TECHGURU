<!-- Dark glass banner with gradient edge; plays nice in GitHub light/dark -->
<p align="center">
  <picture>
    <!-- fallback SVG works in both modes -->
    <img alt="ElevateCRM banner" src="data:image/svg+xml;utf8,
      <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='160' viewBox='0 0 1200 160'>
        <defs>
          <linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
            <stop offset='0%' stop-color='%231FA3FF'/>
            <stop offset='50%' stop-color='%235B5CFF'/>
            <stop offset='100%' stop-color='%238A2BE2'/>
          </linearGradient>
          <linearGradient id='edge' x1='0' y1='0' x2='1' y2='0'>
            <stop offset='0%' stop-color='white' stop-opacity='0.25'/>
            <stop offset='100%' stop-color='white' stop-opacity='0'/>
          </linearGradient>
          <filter id='glass' x='-20%' y='-20%' width='140%' height='140%'>
            <feGaussianBlur stdDeviation='8' result='b'/>
            <feComposite in='SourceGraphic' in2='b' operator='over'/>
          </filter>
        </defs>
        <rect width='1200' height='160' fill='%23121214'/>
        <rect x='24' y='28' rx='16' width='1152' height='104' fill='url(%23g)' opacity='0.14'/>
        <rect x='24' y='28' rx='16' width='1152' height='104' fill='%231C1F23' filter='url(%23glass)'/>
        <rect x='24' y='28' rx='16' width='1152' height='104' fill='none' stroke='url(%23g)' stroke-opacity='0.7'/>
        <rect x='24' y='28' rx='16' width='1152' height='104' fill='none' stroke='url(%23edge)' stroke-width='2'/>
        <g font-family='Segoe UI, Roboto, Helvetica, Arial, sans-serif' fill='white' text-anchor='middle'>
          <text x='600' y='88' font-size='28' font-weight='700'>ElevateCRM + Inventory</text>
          <text x='600' y='116' font-size='14' fill='white' opacity='0.85'>Streamline. Automate. Elevate.</text>
        </g>
      </svg>" />
  </picture>
</p>

<div align="center">
  <img src="assets/logo-elevatecrm.png" alt="ElevateCRM Logo" width="200" />
  <h1>ElevateCRM + Inventory</h1>
  <p><em>Powered by TechGuru</em></p>
  <p><strong>Next-gen CRM & Inventory for teams that hate clunky software.</strong></p>

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
ElevateCRM blends **CRM**, **inventory**, and **automation** with a UI that doesn’t fight you.

---

## 🚀 Features
- **CRM** — Pipelines, notes, tasks, comms timeline  
- **Inventory** — Realtime stock, POs, barcode/QR scanning  
- **Automation** — Celery + Redis workflows  
- **Analytics** — KPIs and dashboards  
- **Desktop** — Electron builds for Win/macOS/Linux

---

## 🛠 Tech Stack
| Layer        | Tools & Frameworks |
|-------------|---------------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend**  | FastAPI, SQLAlchemy 2.x, Redis, Celery |
| **Database** | PostgreSQL (prod), SQLite (dev) |
| **DevOps**   | Docker Compose, Alembic |

---

## 📦 Installation

```bash
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm