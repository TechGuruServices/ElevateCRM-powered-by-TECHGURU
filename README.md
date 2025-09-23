# 🚀 ElevateCRM Management System by TECHGURU

<div align="center">
  <img src="./elevate-logo.png" alt="elevate-logo" width="120" height="120">
  
  **A Modern CRM + Inventory Platform**
  
  **Combining the simplicity of Zoho CRM with the extensibility of Odoo.**

---

## 📋 Table of Contents

- [🌟 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [⚡ Quick Start](#-quick-start)
- [🐳 Docker Setup](#-docker-setup)
- [🛠️ Manual Setup](#️-manual-setup)
- [🌐 API Documentation](#-api-documentation)
- [📱 Frontend Features](#-frontend-features)
- [🔐 Authentication](#-authentication)
- [🚀 Deployment](#-deployment)
- [🧪 Testing](#-testing)
- [📁 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Features

### 🎯 **Core Business Modules**

#### 📊 **Customer Relationship Management (CRM)**
- 360° customer view with complete interaction history
- Advanced customer segmentation and lead scoring
- Automated workflow triggers and follow-ups
- Multi-language and multi-currency support
- Integration with email/calendar systems

#### 📦 **Inventory Management**
- Real-time stock tracking across multiple warehouses
- Barcode/QR scanning capabilities
- Automated reorder triggers with configurable thresholds
- FIFO, LIFO, Weighted Average valuation methods
- Integration with e-commerce platforms (Shopify, WooCommerce, Amazon)

#### 💰 **Sales Pipeline**
- Quote → Order → Invoice → Fulfillment lifecycle
- Drag-and-drop pipeline customization
- Automated approval workflows
- Revenue forecasting and analytics
- Multi-channel sales tracking

### 🛡️ **Enterprise Security**
- **Multi-Factor Authentication** with TOTP/SMS support
- **Row Level Security (RLS)** for multi-tenant isolation
- **JWT-based authentication** with refresh tokens
- **Data encryption** at rest and in transit (AES-256, TLS 1.3)
- **GDPR/CCPA compliance** with data export/deletion

### 🎨 **Modern User Experience**
- **Responsive Design** with mobile-first approach
- **Dark/Light Theme** with user preference persistence
- **Real-time Updates** via WebSockets
- **Offline Capabilities** for mobile apps
- **Accessibility Compliance** (WCAG 2.1 AA)

### 🔌 **Integration Ecosystem**
- **E-commerce Sync**: Shopify, WooCommerce, Amazon
- **Accounting**: QuickBooks, Xero integration
- **Productivity**: Google Workspace, Microsoft 365
- **Payment Processing**: Stripe, PayPal support
- **API-First Design** for custom integrations

---

## 🏗️ Architecture

### **Technology Stack**

#### **Frontend** 🎨
```
Next.js 15 (App Router) + TypeScript
├── UI Framework: Tailwind CSS + shadcn/ui
├── State Management: TanStack Query + Zod validation
├── Forms: React Hook Form
├── Charts: Recharts/ECharts
├── Icons: Lucide React
└── Build Tool: Turbopack
```

#### **Backend** ⚙️
```
FastAPI + Python 3.11+
├── Database: PostgreSQL 16 + SQLAlchemy 2.x
├── Authentication: JWT + OAuth2 + MFA
├── Background Jobs: Celery + Redis
├── File Storage: S3/R2 compatible
├── API Documentation: OpenAPI/Swagger
└── Monitoring: Sentry + OpenTelemetry
```

#### **Infrastructure** 🌐
```
Docker + Docker Compose
├── Database: PostgreSQL with RLS
├── Cache: Redis (sessions, queues)
├── Reverse Proxy: Nginx (production)
├── Monitoring: Prometheus + Grafana
└── CI/CD: GitHub Actions
```

### **Multi-Tenant Architecture**

```
┌─────────────────────────┐
│       Load Balancer     │
└─────────────────────────┘
            │
┌─────────────────────────┐
│      Next.js App        │  
│   (Frontend Routing)    │
└─────────────────────────┘
            │
┌─────────────────────────┐
│      FastAPI Server     │
│   (Tenant Middleware)   │
└─────────────────────────┘
            │
┌─────────────────────────┐
│    PostgreSQL (RLS)     │
│  (Row Level Security)   │
└─────────────────────────┘
```

---

## ⚡ Quick Start

### **Option 1: One-Click Setup (Recommended)**

```bash
# Clone the repository
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

# Start with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Option 2: Development Setup**

```bash
# Prerequisites check
node --version  # v18+ required
python --version  # 3.11+ required
docker --version  # 20+ required

# Quick setup script
./scripts/setup.sh

# Or manual setup (see below)
```

---

## 🐳 Docker Setup

### **Production Deployment**

```bash
# Clone repository
git clone https://github.com/techguru/elevate-crm.git
cd elevate-crm

# Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env.local

# Configure environment variables
nano .env  # Edit database, secrets, etc.

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec backend python app/scripts/seed_data.py

# Create admin user
docker-compose exec backend python scripts/create_admin.py
```

### **Development with Docker**

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Access services
# - Frontend (dev): http://localhost:3000
# - Backend (dev): http://localhost:8000
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

---

## 🛠️ Manual Setup

### **Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Seed initial data
python app/scripts/seed_data.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend Setup**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local with your API endpoints

# Start development server
npm run dev

# Build for production
npm run build
npm start
```

### **Database Setup**

#### **PostgreSQL (Production)**

```bash
# Install PostgreSQL 16
# Windows: Download from postgresql.org
# macOS: brew install postgresql@16
# Ubuntu: sudo apt install postgresql-16 postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE elevatecrm;
CREATE USER elevatecrm_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE elevatecrm TO elevatecrm_user;
\q

# Enable required extensions
sudo -u postgres psql -d elevatecrm
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
\q
```

#### **SQLite (Development)**

```bash
# SQLite is used automatically for development
# No additional setup required
# Database file: backend/elevatecrm.db
```

---

## 🌐 API Documentation

### **Authentication Endpoints**

```http
POST   /api/v1/auth/login           # User login
POST   /api/v1/auth/register        # User registration
POST   /api/v1/auth/refresh         # Refresh JWT token
POST   /api/v1/auth/logout          # User logout
GET    /api/v1/auth/me              # Get current user
```

### **Customer Management**

```http
GET    /api/v1/customers            # List customers
POST   /api/v1/customers            # Create customer
GET    /api/v1/customers/{id}       # Get customer
PUT    /api/v1/customers/{id}       # Update customer
DELETE /api/v1/customers/{id}       # Delete customer
GET    /api/v1/customers/{id}/orders # Get customer orders
```

### **Inventory Management**

```http
GET    /api/v1/products             # List products
POST   /api/v1/products             # Create product
GET    /api/v1/products/{id}        # Get product
PUT    /api/v1/products/{id}        # Update product
DELETE /api/v1/products/{id}        # Delete product
POST   /api/v1/products/{id}/stock  # Update stock
GET    /api/v1/inventory/movements  # Stock movements
```

### **API Usage Examples**

```javascript
// Login and get token
const response = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@company.com',
    password: 'secure_password'
  })
});

const { access_token } = await response.json();

// Use token for authenticated requests
const customers = await fetch('/api/v1/customers', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});
```

### **Interactive API Documentation**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 📱 Frontend Features

### **Modern UI Components**

```typescript
// Button variants
<Button variant="default">Primary Action</Button>
<Button variant="outline">Secondary Action</Button>
<Button variant="ghost">Subtle Action</Button>

// Status badges
<Badge variant="success">Active</Badge>
<Badge variant="warning">Low Stock</Badge>
<Badge variant="destructive">Out of Stock</Badge>

// Data cards
<Card>
  <CardHeader>
    <CardTitle>Revenue</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">$24,500</div>
  </CardContent>
</Card>
```

### **Responsive Dashboard**

- **Desktop**: Full sidebar with navigation, stats cards, data tables
- **Tablet**: Collapsible sidebar, responsive grid layouts
- **Mobile**: Bottom navigation, stacked cards, drawer menus

### **Theme System**

```typescript
// Dark/Light mode toggle
const { theme, setTheme } = useTheme();

// Theme-aware components
<div className="bg-white dark:bg-slate-900">
  <h1 className="text-slate-900 dark:text-white">
    Dynamic Content
  </h1>
</div>
```

---

## 🔐 Authentication

### **Multi-Factor Authentication**

```python
# Backend: Enable MFA for user
@router.post("/auth/mfa/enable")
async def enable_mfa(user: User = Depends(get_current_user)):
    secret = pyotp.random_base32()
    # Generate QR code for authenticator app
    return {"secret": secret, "qr_code": generate_qr_code(secret)}

# Verify TOTP token
@router.post("/auth/mfa/verify")
async def verify_mfa(token: str, user: User = Depends(get_current_user)):
    totp = pyotp.TOTP(user.mfa_secret)
    return {"valid": totp.verify(token)}
```

### **JWT Token Management**

```typescript
// Frontend: Automatic token refresh
export class AuthService {
  private refreshToken = () => {
    // Automatically refresh tokens before expiry
    const token = localStorage.getItem('refresh_token');
    return fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  };
}
```

### **Row Level Security (RLS)**

```sql
-- Database: Tenant isolation
CREATE POLICY tenant_isolation ON customers
    FOR ALL TO authenticated_users
    USING (company_id = current_setting('app.current_tenant_id')::uuid);

-- Enable RLS
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
```

---

## 🚀 Deployment

### **Production Environment Variables**

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/elevatecrm
SECRET_KEY=your-super-secret-key-here
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
STRIPE_SECRET_KEY=sk_live_...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://api.yourcompany.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### **Cloud Deployment Options**

#### **Vercel (Frontend) + Railway (Backend)**
```bash
# Deploy frontend to Vercel
npx vercel --prod

# Deploy backend to Railway
railway login
railway link
railway up
```

#### **Digital Ocean App Platform**
```yaml
# .do/app.yaml
name: elevatecrm
services:
- name: frontend
  source_dir: frontend
  github:
    repo: your-repo/elevatecrm
    branch: main
  run_command: npm start
  
- name: backend
  source_dir: backend
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
```

---

## 🧪 Testing

### **Backend Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

### **Frontend Testing**

```bash
# Unit tests with Jest
npm test

# E2E tests with Playwright
npm run test:e2e

# Build test
npm run build
```

---

## 📁 Project Structure

```
elevate-crm/
├── 📁 frontend/                    # Next.js 15 frontend application
│   ├── 📁 app/                     # App Router pages
│   │   ├── 📁 auth/                # Authentication pages
│   │   ├── 📁 dashboard/           # Dashboard pages
│   │   ├── 📁 customers/           # Customer management
│   │   └── 📁 inventory/           # Inventory management
│   ├── 📁 components/              # Reusable UI components
│   │   ├── 📁 ui/                  # shadcn/ui components
│   │   └── 📁 layout/              # Layout components
│   ├── 📁 lib/                     # Utilities and helpers
│   └── 📁 styles/                  # Global styles and themes
│
├── 📁 backend/                     # FastAPI backend application
│   ├── 📁 app/                     # Main application code
│   │   ├── 📁 api/                 # API routes
│   │   │   └── 📁 v1/              # API version 1
│   │   ├── 📁 core/                # Core functionality
│   │   ├── 📁 models/              # SQLAlchemy models
│   │   ├── 📁 schemas/             # Pydantic schemas
│   │   ├── 📁 services/            # Business logic
│   │   └── 📁 middleware/          # Custom middleware
│   ├── 📁 migrations/              # Alembic database migrations
│   └── 📁 scripts/                 # Utility scripts
│
├── 📄 docker-compose.yml           # Development environment
├── 📄 docker-compose.dev.yml       # Development with hot reload
├── 📄 .env.example                 # Environment template
└── 📄 README.md                    # This file
```

---

## 🚀 Standalone Application Setup

### **Option 1: Single Machine Deployment**

```bash
# 1. Download and extract the application
wget https://github.com/techguru/elevate-crm/archive/main.zip
unzip main.zip
cd elevate-crm-main

# 2. Run the automatic setup script
chmod +x scripts/standalone-setup.sh
./scripts/standalone-setup.sh

# 3. Access your application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### **Option 2: Windows Standalone**

```powershell
# 1. Download PowerShell setup script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/techguru/elevate-crm/main/scripts/setup-windows.ps1" -OutFile "setup.ps1"

# 2. Run setup (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1

# 3. Start services
.\scripts\start-windows.bat
```

---

## 🆘 Support & Documentation

### **Getting Help**
- 📚 [Full Documentation](./docs/)
- 🎯 [API Reference](http://localhost:8000/docs)
- 💬 [Community Discord](https://discord.gg/techguru)
- 🐛 [Bug Reports](https://github.com/techguru/elevate-crm/issues)

### **Questions/Support**
- 📧 Email: info@techguruofficial.us
- 🌐 Website: https://techguruofficial.us
- 📞 Phone: +1 (786) 636-9964

---

<div align="center">
  <h3>🌟 Star this repository if you find it helpful! 🌟</h3>
  
  **Built with ❤️ by TECHGURU**
  
  [🌐 Website](https://techguruofficial.us) • [📧 Contact](info@techguruofficial.us)
</div>
