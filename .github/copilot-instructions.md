# TECHGURU CRM + Inventory Platform - AI Coding Instructions

Name of the project: ElevateCRM Management System by TECHGURU

TECHGURU logo and icon file name 'techguru_logo.png', 'techguru_icon.ico' must be used in the application.

## Project Overview
You are building a modern CRM + Inventory platform that combines the simplicity of Zoho CRM with the extensibility of Odoo. Target users are small-to-medium businesses needing unified customer management and inventory tracking.

## Architecture Principles

### Core Design Patterns
- **Modular Architecture**: Each business domain (CRM, Inventory, Sales, etc.) should be separate, independently deployable modules
- **Multi-tenancy**: Support white-label deployment with tenant-specific configurations
- **API-First**: All functionality exposed via REST/GraphQL APIs for mobile and third-party integrations
- **Event-Driven**: Use event sourcing for audit trails and real-time updates across modules

### Technology Stack (Production Ready)
- **Frontend**: Next.js 14+ (App Router), TypeScript, Tailwind CSS, shadcn/ui, Radix UI
- **State Management**: TanStack Query, Zod validation, React Hook Form
- **Charts & Tables**: Recharts/ECharts for visualization, Ag-Grid for heavy data tables
- **Backend**: FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.x, Alembic migrations
- **Database**: PostgreSQL (RLS, Full-Text Search, JSONB, schemas), Redis (cache, WebSocket pub/sub, rate limiting)
- **Background Jobs**: Celery/Dramatiq workers for integrations, emails, webhooks, bulk imports
- **Storage**: S3/Cloudflare R2 for files and exports with signed URLs
- **Real-time**: WebSockets with Redis pub/sub for live inventory updates
- **Authentication**: Keycloak (self-hosted) or Auth0/Supabase (managed) with OIDC/OAuth2, MFA
- **Monitoring**: Sentry (FE/BE), OpenTelemetry for distributed tracing

## Key Business Domains

### 1. Inventory Management
- Real-time stock tracking across multiple warehouses and sales channels
- Barcode/QR scanning capabilities for mobile apps
- Automated reorder triggers based on configurable thresholds
- Integration patterns for e-commerce platforms (Shopify, WooCommerce, Amazon)

### 2. Customer Relationship Management  
- 360° customer view combining contact info, purchase history, communications
- Segmentation engine for targeted marketing campaigns
- Lead scoring algorithms with AI-powered recommendations
- Integration with email/calendar systems (Google Workspace, Microsoft 365)

### 3. Sales Pipeline
- Quote → Order → Invoice → Fulfillment lifecycle management
- Drag-and-drop pipeline customization per business type
- Automated workflow triggers for follow-ups and approvals
- Multi-currency and multi-language support

## Development Guidelines

### Code Organization & Quick Start
```
frontend/                    # Next.js 14+ app
  ├── app/                  # App Router pages
  ├── components/           # shadcn/ui + custom components  
  ├── lib/                 # Utils, API clients, auth
  └── types/               # Zod schemas & TypeScript types

backend/                     # FastAPI application
  ├── app/
  │   ├── api/             # API routes by version
  │   ├── models/          # SQLAlchemy models
  │   ├── schemas/         # Pydantic models
  │   ├── services/        # Business logic layer
  │   └── integrations/    # External API connectors
  ├── migrations/          # Alembic database migrations
  └── workers/             # Celery task definitions

docker-compose.dev.yml       # PostgreSQL, Redis, Keycloak for development
```

### Bootstrap Commands
```bash
# Frontend setup
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend && npx shadcn-ui@latest init

# Backend setup  
mkdir backend && cd backend
pip install fastapi[all] sqlalchemy[postgresql] alembic celery[redis]
fastapi dev app/main.py
```

### API Design Standards
- Use consistent RESTful patterns: GET /api/v1/customers, POST /api/v1/orders
- Implement pagination with `limit`, `offset`, and `total_count` metadata
- Standard error responses with error codes and user-friendly messages
- Rate limiting and request/response logging for security

### UI/UX Requirements
- Support both dark and light themes with user preference persistence
- Mobile-first responsive design with offline capabilities
- Customizable dashboards with drag-and-drop widgets
- Accessibility compliance (WCAG 2.1 AA standards)

### Security & Compliance
- Multi-factor authentication with TOTP/SMS options
- Role-based access control (RBAC) with granular permissions
- Data encryption at rest and in transit (AES-256, TLS 1.3)
- GDPR/CCPA compliance with data export and deletion capabilities

### Integration Patterns & External APIs
- **E-commerce Sync**: Shopify, WooCommerce, Amazon (products, inventory, orders)
- **Accounting**: QuickBooks/Xero sync for invoices/bills, optional Stripe checkout links
- **Productivity**: Google Workspace & Microsoft 365 (calendar, email, contacts)
- **Architecture**: Outbox table + Celery workers for reliable webhooks
- **Authentication**: OAuth2 per-integration with scoped tokens and signature verification
- **Resilience**: Circuit breaker pattern, exponential backoff with tenacity library
- **File Storage**: boto3 to R2/S3 with signed URLs, automatic CDN invalidation

## Database Schema & Multi-Tenant Design

### Core Data Model (PostgreSQL + RLS)
```sql
-- Tenant isolation with Row Level Security
CREATE TABLE companies (id, name, subdomain, settings JSONB);
CREATE TABLE users (id, company_id, email, roles[], tenant_id);

-- CRM Entities (industry-agnostic)
CREATE TABLE contacts (id, company_id, type, properties JSONB);
CREATE TABLE accounts (id, company_id, contact_id, lifecycle_stage);
CREATE TABLE opportunities (id, company_id, contact_id, pipeline_stage, value);

-- Universal Product/Service Model  
CREATE TABLE products (id, company_id, sku, type, properties JSONB);
CREATE TABLE stock_locations (id, company_id, name, address);
CREATE TABLE stock_moves (id, product_id, from_location, to_location, qty, cost);

-- Order Lifecycle (Quote → Sales → Invoice → Fulfillment)
CREATE TABLE orders (id, company_id, type, stage, line_items JSONB);
CREATE TABLE invoices (id, order_id, status, payment_terms, due_date);
```

### Naming Conventions & Patterns
- **Tables**: snake_case, plural nouns (`stock_moves`, `order_line_items`)  
- **Columns**: snake_case, descriptive (`created_at`, `external_ref_id`)
- **Indexes**: `idx_table_column` for single, `idx_table_col1_col2` for composite
- **JSONB Fields**: Use for flexible properties that vary by industry/tenant
- **Audit**: `created_at`, `updated_at`, `created_by_id` on all business entities

## Business Logic Considerations

### Industry-Agnostic Flexibility
- **Configurable Pipelines**: Sales stages, approval workflows customizable per tenant
- **Dynamic Properties**: JSONB fields for industry-specific data (project phases, case details)
- **Flexible Pricing**: Support hourly rates, project-based, subscription, and product pricing
- **Multi-Entity Support**: Handle B2B (accounts/contacts), B2C (individuals), and hybrid models

### Inventory & Fulfillment Rules
- **Valuation Methods**: FIFO, LIFO, Weighted Average configurable per company
- **Stock Policies**: Allow negative stock, reservation system, auto-reorder triggers
- **Multi-Location**: Warehouse transfers, optimized picking, cycle count scheduling
- **Service Industries**: Time-based inventory (consultant hours, equipment rental)

### Workflow Automation & AI Features
- **Visual Builder**: Drag-and-drop automation for follow-ups, approvals, notifications
- **Smart Segmentation**: AI-powered customer classification and lead scoring
- **Demand Forecasting**: ML models using sales history + seasonality patterns
- **Voice Input**: Speech-to-text for mobile field updates and quick note-taking

## Performance & Scalability

### Caching Strategy
- Redis for session management and frequently accessed data
- CDN for static assets and user-uploaded files
- Database query optimization with proper indexing
- API response caching with cache invalidation strategies

### Monitoring & Observability
- Application performance monitoring (APM) integration
- Structured logging with correlation IDs for request tracing
- Health check endpoints for all microservices
- Business metrics dashboards for key performance indicators

## Step-by-Step Development Plan

### Phase 1: Foundation
```bash
# 1. Bootstrap repos with docker-compose.dev.yml (PostgreSQL, Redis, Keycloak)
# 2. Auth & tenants - OIDC integration with tenant_id claims + RLS
# 3. Core data model: Companies/Users/Roles, Contacts/Accounts, Products/Stock
```

### Phase 2: Core Features  
```bash
# 1. Global shell (sidebar, theme toggle), entity grids with filters/saved views
# 2. Sales pipeline board, inventory overview, order creation wizard
# 3. First integration: Shopify (products, inventory sync, order import)
```

### Phase 3: Automation & Advanced Features
```bash
# 1. Outbox pattern + Celery workers for reliable webhooks/email/integrations
# 2. QuickBooks/Xero accounting sync, optional Stripe payment links
# 3. Visual workflow builder, AI lead scoring, demand forecasting
```

## Testing & Quality Standards
- **Python**: Ruff + Black formatting, Pytest + Coverage (>80% business logic)
- **TypeScript**: ESLint + Prettier, Playwright for E2E testing
- **Performance**: Load test critical endpoints (orders, stock moves, bulk imports)
- **Security**: Regular dependency updates, secret rotation, audit trail validation

## Security & Compliance (2025 Standards)
- **Multi-Factor Auth**: TOTP/SMS with backup codes, conditional access policies
- **Data Isolation**: PostgreSQL RLS + per-tenant encryption keys in vault
- **File Security**: Signed URLs with expiration, automatic virus scanning
- **Audit Trails**: Immutable logs for orders, stock moves, invoices, user actions
- **GDPR/CCPA**: Automated data export, deletion workflows, consent management

When implementing features, prioritize **configurability over hard-coding** to support diverse industries (retail, consulting, manufacturing, software sales, healthcare, legal). Always implement **tenant isolation** at the database level and ensure **API endpoints respect user permissions** through middleware validation.
