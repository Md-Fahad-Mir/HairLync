<div align="center">

# ✂️ HairLync

**The all-in-one platform connecting clients with barbers, hairdressers, and salons —**
**powered by AI hair analysis, smart booking, and multi-channel subscriptions.**

[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](services/backend)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](services/landing)
[![FastAPI](https://img.shields.io/badge/FastAPI-AI%20Service-009688?logo=fastapi&logoColor=white)](services/ai)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?logo=stripe&logoColor=white)](services/backend/Apps/subscriptions)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](deployment/compose)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)](infrastructure/terraform)

</div>

---

## 🎬 Demo

<div align="center">

<video src="media%20file/video.webm" controls muted width="720">
  Your browser does not support inline video playback.
  <a href="media file/video.webm">Watch the demo video</a>.
</video>

📹 If the player above doesn't render, [watch/download the demo video directly](<media file/video.webm>).

</div>

---

## 📖 Overview

HairLync is a full-stack marketplace that helps **clients** discover and book appointments with **barbers, hairdressers, and salons**, while giving professionals the tools to manage their business — portfolios, services, bookings, employees, and subscriptions.

An **AI hair-analysis engine** gives clients personalized style recommendations, and a **multi-channel subscription system** (Stripe today, Apple/Google App Store ready) powers premium features for professionals.

The repository is a monorepo containing every service that makes up the product: the API, the marketing site, the internal admin dashboard, the AI microservice, and all infrastructure-as-code needed to run it in production.

---

## 🏗️ Architecture

```text
                              ┌─────────────────────┐
                              │   Landing Page      │  hairlync.com
                              │   (React + Vite)    │  Marketing, sign-up, pricing
                              └──────────┬──────────┘
                                         │
                              ┌──────────┴───────────┐
                              │   Admin Dashboard    │  admin.hairlync.com
                              │   (React + Vite)     │  Internal operations UI
                              └──────────┬───────────┘
                                         │  REST / JWT
                    ┌────────────────────┴────────────────────┐
                    │                                         │
          ┌─────────┴─────────┐                      ┌────────┴─────────┐
          │  Backend API      │  ───── calls ────▶   │  AI Service      │
          │  (Django + DRF)   │                      │  (FastAPI)       │
          │  api.hairlync.com │  ◀──── analysis ───  │  ai.hairlync.com │
          └─────────┬─────────┘                      └──────────────────┘
                    │
        ┌───────────┼────────────┐
        │           │            │
   ┌────┴───┐  ┌────┴────┐  ┌────┴───────┐
   │Postgres│  │  Stripe │  │  AWS S3    │
   │  RDS   │  │ Payments│  │+ CloudFront│
   └────────┘  └─────────┘  └────────────┘
```

Every service ships as its own Docker image and is orchestrated with Docker Compose locally, and via Terraform + Ansible + GitHub Actions in staging/production on AWS.

---

## 📦 Monorepo Layout

```text
HairLync/
├── services/
│   ├── backend/        # Django REST API — the system of record
│   ├── ai/              # FastAPI hair-analysis microservice
│   ├── landing/         # Public marketing site (React + Vite + Tailwind)
│   └── admin/            # Internal admin dashboard (React + Vite)
│
├── deployment/
│   ├── compose/          # Docker Compose files (base / local / staging / production)
│   ├── environments/     # Per-service env templates for each environment
│   ├── nginx/             # Reverse-proxy configuration
│   ├── monitoring/       # Observability stack
│   └── scripts/           # Deploy, rollback, and server-configuration scripts
│
├── infrastructure/
│   ├── terraform/          # AWS infrastructure as code (VPC, RDS, ECS/EC2, S3, CloudFront…)
│   ├── ansible/            # Server provisioning/configuration
│   └── iam/                 # IAM roles & policies
│
├── docs/                   # Architecture write-ups, runbooks, and guides
└── Makefile                # One-command entry point for common workflows
```

---

## ✨ Core Features

### For Clients
- 🔍 Discover barbers, hairdressers, and salons by location, category, and rating
- 📅 Real-time appointment booking with live availability
- 🤖 AI-powered hair analysis and personalized style recommendations
- ⭐ Reviews, ratings, and favorites
- 📚 Access to educational styling content

### For Barbers, Hairdressers & Salons
- 👤 Rich portfolio management — barbers, salons, *and* salon employees can each showcase their own work
- 🧑‍🤝‍🧑 Salon employee sub-profiles with scoped, restricted access
- 🗓️ Booking, timeslot, and business-status management
- 💳 Subscription-gated premium features (AI recommendations, analytics, educational content)
- 📈 Business analytics and client insights

### Platform
- 🔐 JWT authentication with role-based access control (client / barber / salon / admin)
- 💰 **Multi-channel subscriptions** — Stripe Checkout & Billing Portal today, with a schema ready for Apple App Store and Google Play in-app purchases
- 🪝 Idempotent, signature-verified Stripe webhooks as the single source of truth for entitlement
- 🖥️ Internal admin dashboard for platform operations
- ☁️ AWS-native media storage via S3 + CloudFront CDN

---

## 🧰 Tech Stack

| Layer | Stack |
|---|---|
| **Backend API** | Django 6, Django REST Framework, SimpleJWT, drf-yasg (Swagger/OpenAPI) |
| **AI Service** | FastAPI, OpenAI / Anthropic APIs, Pillow, NumPy |
| **Landing Page** | React 19, Vite, Tailwind CSS, Framer Motion |
| **Admin Dashboard** | React, Vite, MUI, Radix UI, Tailwind CSS |
| **Payments** | Stripe (Checkout, Billing Portal, Webhooks) |
| **Database** | PostgreSQL (SQLite for local dev) |
| **Storage** | AWS S3 + CloudFront |
| **Infra** | Docker, Docker Compose, Terraform, Ansible, Nginx |
| **CI/CD** | GitHub Actions |

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager, backend/AI services)
- Node.js 20+ (for landing/admin local development outside Docker)

### Run everything locally

```bash
git clone <repo-url>
cd HairLync

# Copy environment templates and fill in local values
cp deployment/environments/backend.env.example deployment/environments/.env.local.backend
cp deployment/environments/landing.env.example  deployment/environments/.env.local.landing
cp deployment/environments/admin.env.example    deployment/environments/.env.local.admin

# Start the full stack (backend, AI, landing, admin)
make up-local
```

| Service | URL |
|---|---|
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs/ |
| AI Service | http://localhost:8001 |
| Landing Page | http://localhost:3000 |
| Admin Dashboard | http://localhost:3001 |

### Run the backend standalone

```bash
cd services/backend
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

### Run the test suite

```bash
cd services/backend
uv run python manage.py test Apps.users.tests Apps.bookings.tests Apps.profiles.tests Apps.subscriptions.tests
```

---

## 💳 Subscriptions & Payments

Subscription logic lives in [`services/backend/Apps/subscriptions/`](services/backend/Apps/subscriptions/) and is designed to support **multiple payment channels** behind one consistent entitlement model (`CustomUserModel.paid_user`, `current_plan`, `current_period_end`, `is_subscribed()`).

| Channel | Status |
|---|---|
| **Stripe** (landing page checkout) | ✅ Implemented — Checkout Sessions, Billing Portal, signature-verified & idempotent webhooks |
| **Apple App Store** (in-app purchase) | 🧩 Schema ready (`platform` field) — not yet implemented |
| **Google Play** (in-app purchase) | 🧩 Schema ready (`platform` field) — not yet implemented |

Key endpoints:

```
GET  /api/v1/subscriptions/plans/                   List available plans
POST /api/v1/subscriptions/stripe/checkout/          Start a Stripe Checkout session
POST /api/v1/subscriptions/stripe/webhook/            Stripe webhook receiver (source of truth)
POST /api/v1/subscriptions/stripe/billing-portal/     Manage/cancel an active Stripe subscription
GET  /api/v1/subscriptions/my/                         Current subscription status
GET  /api/v1/subscriptions/history/                    Subscription history
```

Stripe webhooks (`checkout.session.completed`, `customer.subscription.*`, `invoice.paid`, `invoice.payment_failed`) are the **only** path that activates paid access — never the client redirect — with every event ID recorded exactly once to guarantee idempotent processing under retries.

---

## 🛠️ Deployment

Deployment is driven by the [`Makefile`](Makefile), Terraform, Ansible, and GitHub Actions:

```bash
make tf-plan   ENV=production        # Preview infrastructure changes
make tf-apply  ENV=production        # Provision AWS infrastructure
make ansible-prod                    # Configure the production server
make deploy-prod                     # Build, push, and roll out all services
make rollback  TAG=<sha>             # Roll back to a previous image
```

See [`docs/deployment-guide.md`](docs/deployment-guide.md), [`docs/infrastructure-guide.md`](docs/infrastructure-guide.md), and [`docs/disaster-recovery.md`](docs/disaster-recovery.md) for the full operational playbook.

---

## 📚 Documentation

| Doc | Description |
|---|---|
| [`docs/deployment-guide.md`](docs/deployment-guide.md) | End-to-end deployment walkthrough |
| [`docs/infrastructure-guide.md`](docs/infrastructure-guide.md) | AWS infrastructure overview |
| [`docs/admin-dashboard-guide.md`](docs/admin-dashboard-guide.md) | Admin dashboard usage guide |
| [`docs/cloudfront-media.md`](docs/cloudfront-media.md) | Media storage & CDN setup |
| [`docs/disaster-recovery.md`](docs/disaster-recovery.md) | Backup & recovery procedures |
| [`docs/selective-deployment.md`](docs/selective-deployment.md) | Path-based CI/CD deployment strategy |
| [`docs/devops-architectural-blog.md`](docs/devops-architectural-blog.md) | Architecture deep-dive |
| [`docs/devops-production-walkthrough.md`](docs/devops-production-walkthrough.md) | Production operations walkthrough |
| [`PAYMENT_SYSTEM_CURRENT_FLOW_ANALYSIS.md`](PAYMENT_SYSTEM_CURRENT_FLOW_ANALYSIS.md) | Full technical audit of the payment system |

Interactive API documentation is available at `/api/docs/` (Swagger UI) and `/api/redoc/` on any running backend instance.

---

## 🔐 Environment Variables

Each service has an `.env.example` template describing its configuration:

- [`services/backend/.env.example`](services/backend/.env.example)
- [`deployment/environments/backend.env.example`](deployment/environments/backend.env.example)
- [`deployment/environments/landing.env.example`](deployment/environments/landing.env.example)
- [`deployment/environments/admin.env.example`](deployment/environments/admin.env.example)
- [`deployment/environments/ai.env.example`](deployment/environments/ai.env.example)

Never commit filled-in `.env` files — copy the templates and keep real secrets out of version control.

---

<div align="center">

Built with ❤️ by the HairLync team

</div>
