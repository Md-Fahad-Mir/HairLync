# Terraform Meets Ansible: Automating HairIQ's Multi-Service Observability & Deployment on AWS

> "The difference between amateur and professional software engineering is the repeatability of your deployment." 
> 
> As developers, we love writing code, but shipping it reliably to production is where the real engineering begins. In this deep dive, we'll walk through how we modularized, automated, and secured the infrastructure and configuration deployment pipelines for **HairIQ**—a multi-service application consisting of a Django REST backend, a FastAPI AI processing service, and Next.js frontends.

---

## 🚀 Introduction

Moving a multi-service application from "it works on my machine" to a highly resilient, isolated, and scalable environment in the cloud is a classic DevOps challenge. 

Historically, developers fell into two traps:
1. **The Snowflake Server:** Setting up cloud instances manually by SSHing into them, installing packages, editing config files directly, and hoping they never crash.
2. **Configuration Drift:** When the staging server behaves differently from the production server because of undocumented package updates or hidden environment variables.

To solve this for HairIQ, we built a standardized, declarative, infrastructure-as-code (IaC) deployment pipeline. By separating the **infrastructure provisioning** (via Terraform) from the **software configuration** (via Ansible) and wrapping everything in lightweight **Docker containers** behind an **Nginx reverse proxy**, we achieved a setup that can spin up an identical clone of our production stack in staging or development in under 10 minutes.

---

## ⚙️ Pre-Requisites & Tech Stack Overview

To run and manage this architecture, our pipeline uses a battle-tested stack of modern infrastructure engineering tools:

*   **Infrastructure Provisioning:** [Terraform](https://www.terraform.io/) (v1.5+) manages our stateful AWS resources (EC2 compute, RDS PostgreSQL database, and S3 media storage).
*   **Configuration Management:** [Ansible](https://www.ansible.com/) (v2.15+) configures the OS, installs the container runtime, provisions SSL certs via Certbot, and drops environment-specific configurations.
*   **Orchestration & Containerization:** [Docker & Docker Compose](https://www.docker.com/) package each individual microservice into lightweight, sandboxed units.
*   **Ingress & Routing:** [Nginx](https://www.nginx.com/) acts as our reverse-proxy, TLS termination endpoint, rate-limiter, and static asset server.
*   **Package Management:** [Astral `uv`](https://github.com/astral-sh/uv) handles the Django backend's Python dependencies with blazing-fast speeds.

```
                  ┌──────────────────────────────┐
                  │          HTTP/HTTPS          │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │    Nginx Reverse Proxy       │
                  │   (TLS, Rates, Headers)      │
                  └──────┬──────┬──────┬──────┬──┘
                         │      │      │      │
      ┌──────────────────┘      │      │      └─────────────────┐
      │ :3000                   │ :8000│ :8001                  │ :3001
┌─────▼────────┐          ┌─────▼──────▼┐    ┌▼─────────────┐     ┌─▼────────────┐
│ hairiq-      │          │ hairiq-     │    │ hairiq-ai    │     │ hairiq-admin │
│ landing      │          │ backend     │    │ (FastAPI)    │     │ (Next.js)    │
│ (Next.js)    │          │ (Django)    │    └──────┬───────┘     └──────────────┘
└──────────────┘          └──────┬──────┘           │
                                 ├───────────┐      │
                                 ▼           ▼      ▼
                            ┌────────┐   ┌─────────────┐
                            │ AWS S3 │   │   AWS RDS   │
                            │ Bucket │   │ (PostgreSQL)│
                            └────────┘   └─────────────┘
```

---

## 📁 Project & Directory Architecture

To decouple the application's business logic from its infrastructure configurations, the project is structured as a monorepo split into code (`services/`) and deployment modules (`deployment/` and `infrastructure/`):

```
HairIQ/
├── Makefile                          # Unified build and deploy CLI
├── .github/
│   └── workflows/
│       ├── deploy.yml                # Main production CI/CD pipeline
│       ├── staging-deploy.yml        # Staging CI/CD pipeline
│       └── pr-checks.yml             # Pull Request syntax & lint validator
├── deployment/
│   ├── .gitignore                    # Prevents secrets/states leaks
│   ├── compose/
│   │   ├── docker-compose.base.yml   # Shared service & health definitions
│   │   ├── local/
│   │   │   └── docker-compose.yml    # Dev override with hot-reload mounts
│   │   ├── staging/
│   │   │   └── docker-compose.yml    # Staging image specs
│   │   └── production/
│   │       └── docker-compose.yml    # Production production-ready images
│   ├── environments/
│   │   ├── backend.env.example       # Django settings template
│   │   └── ai.env.example            # OpenAI/Anthropic settings template
│   ├── nginx/
│   │   ├── production/
│   │   │   └── app.conf              # Production Nginx server blocks
│   │   └── shared/
│   │       ├── proxy-params.conf     # Standardized upstream headers
│   │       ├── rate-limiting.conf    # Route-specific limit definitions
│   │       └── security-headers.conf # CSP, XSS, Frame Options
│   └── scripts/
│       ├── deploy.sh                 # Unified pipeline execution orchestrator
│       ├── configure-server.sh       # Executable Ansible entrypoint
│       ├── terraform-apply.sh        # Infrastructure creation wrapper
│       └── rollback.sh               # Quick tag rollback utility
└── infrastructure/
    ├── ansible/
    │   ├── group_vars/
    │   │   ├── all.yml               # Global variables (domain, services)
    │   │   └── production.yml        # Production email and override vars
    │   ├── inventories/
    │   │   └── production/
    │   │       └── hosts             # Targets dynamic public IP of server
    │   ├── playbooks/
    │   │   └── site.yml              # Base orchestrating playbook
    │   └── roles/
    │       ├── docker/               # Engine installer tasks
    │       ├── nginx/                # Config deployment tasks
    │       └── app-deploy/           # Directory setup and Compose execution
    └── terraform/
        ├── shared/
        │   ├── main.tf               # EC2, EIP, S3, RDS configurations
        │   └── variables.tf          # Global variables and defaults
        └── environments/
            └── production/
                └── main.tf           # Env-specific module overrides
```

---

## 🧩 The Step-by-Step Deep Dive

Let’s trace the pipeline of how a raw commit becomes a secure, live service running on AWS.

### 📦 1. Fast Dependencies and Docker Optimization

One of the biggest issues in standard Python Docker builds is the install time. If a single file changes in your application, Docker has to re-run your `pip install` commands from scratch unless they are strictly separated. 

For the **Django Backend**, we leveraged `uv` for package management and separated the build into a **multi-stage pipeline**. Let's review the `deployment/services/backend/Dockerfile`:

```dockerfile
# ─── Stage 1: Builder ────────────────────────────────────────────────
FROM python:3.13-slim-bookworm AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export requirements and install dependencies
RUN uv export --no-dev --frozen > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==22.0.0 uvicorn[standard]==0.30.0 psycopg2-binary>=2.9.10
```

#### Why is this efficient?
*   **Docker Layer Caching:** The files `pyproject.toml` and `uv.lock` are copied *before* the application code. Since these files rarely change, Docker completely skips installing dependencies on subsequent code modifications, reducing build times from minutes to seconds.
*   **Multi-Stage Build:** In Stage 2 (the runtime stage), we copy only the compiled dependencies (`site-packages`) and the application code. This excludes `uv`, caches, compiler utilities, and unnecessary system packages, keeping our final image size slim and secure.

---

### 🧱 2. Provisioning Infrastructure with Terraform

The infrastructure is declared in Terraform. Let's look at how the resources are composed inside `infrastructure/terraform/shared/main.tf`:

```hcl
# AWS Key Pair
resource "aws_key_pair" "deploy_key" {
  key_name   = "${var.project_name}-${var.environment}-key"
  public_key = file(pathexpand(var.public_key_path))
}

# EC2 Instance
resource "aws_instance" "app_server" {
  ami                    = var.ami
  instance_type          = var.instance_type
  key_name               = aws_key_pair.deploy_key.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
}
```

Terraform also spawns our **RDS PostgreSQL** database (isolated inside the private security group scope, accessible only from the EC2 instance via dynamic firewall referencing) and our public-read **S3 Media Storage Bucket** where customer hair pictures are uploaded and served.

---

### 🔄 3. Dynamic Configuration via Ansible

Once Terraform provisions the hardware, we need to configure it. We execute Ansible using a wrapper shell script. Here's a look at our playbooks mapping in `infrastructure/ansible/playbooks/site.yml`:

```yaml
- hosts: webservers
  become: true

  vars_files:
    - ../group_vars/all.yml
    - "../group_vars/{{ env }}.yml"

  roles:
    - role: docker
    - role: nginx
    - role: app-deploy
    - role: certbot
```

This sequence automates the system bootstrap steps:
1.  **`docker`**: Downloads GPG keys, sets up the repository codename fallback (e.g., `noble` fallback for Ubuntu 24.04), and installs the container runtimes.
2.  **`nginx`**: Deploys rate limiting limits, proxy parameters, and site definitions.
3.  **`app-deploy`**: Securely places our `.env` files and `docker-compose.prod.yml` in `/home/ubuntu/hairiq`.
4.  **`certbot`**: Handles Let's Encrypt certificates automatically for all five subdomains (`hairlync.com`, `www`, `api`, `ai`, and `admin`).

---

### 🛡️ 4. Reverse Proxying, Upload Allowances & Rate Limiting

Our Nginx setup acts as a protective shield. Let's inspect `deployment/nginx/production/app.conf` for the **AI service**:

```nginx
# AI Service (FastAPI — Hair Analysis)
server {
    listen 80;
    server_name ai.{{DOMAIN}};
    client_max_body_size 20M;

    include /etc/nginx/conf.d/security-headers.conf;

    location / {
        include /etc/nginx/conf.d/proxy-params.conf;
        proxy_pass http://localhost:8001;
        limit_req zone=ai_limit burst=5 nodelay;

        # Extended timeout for AI image analysis
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
```

Notice two critical production configurations here:
1.  **Extended Timouts:** Large-language model requests or vision-based hair analysis queries can take tens of seconds to respond. We set `proxy_read_timeout 120s` to prevent Nginx from returning standard `504 Gateway Timeout` errors early.
2.  **Route-Specific Rate Limiting:** We set a specialized rate-limiting zone `ai_limit` in `rate-limiting.conf`:

```nginx
# AI analysis rate limit: more restrictive (expensive LLM operations)
limit_req_zone $binary_remote_addr zone=ai_limit:10m rate=3r/s;
```

This prevents malicious script scraping from exhausting GPU compute allocations.

---

## 🌐 Testing & Verifying the Setup

Testing a complex pipeline should not require push-to-production cycles. Here is how you can validate the configurations locally:

### 1. Spin up the Local Dev Stack
Run the make shortcut from the root directory to build and start the environment:
```bash
make up-local
```
This command reads the local overrides, builds images from source, mounts your working directories into the container runtime directories, and runs hot-reload servers.

### 2. Verify Health Endpoints
Open a new terminal window and run HTTP client checks against the services:
```bash
# Verify the FastAPI AI Service Health Endpoint
curl -i http://localhost:8001/health

# Verify the Django Backend Admin Route
curl -i http://localhost:8000/admin/
```

Expected output should confirm `HTTP/1.1 200 OK` (or appropriate redirects) along with application health responses.

---

## 💡 Conclusion & DevOps Mindset

By committing our deployment setups as code, we gained key structural advantages:
*   **Self-Documentation:** The repository structure itself documents how services connect, what ports they expose, and what credentials they require.
*   **Infrastructure Reproducibility:** We can tear down staging and bring it back up dynamically using `make deploy-staging` without leaving orphaned files or custom package deviations.
*   **Robust Security Defaults:** Containers execute under unprivileged user privileges (`USER appuser`), RDS PostgreSQL stays completely hidden from the public internet, and Nginx isolates backend runtimes behind optimized security filters.

As you iterate on your applications, treat your deployment automation with the same care as your application code. Happy deploying! 🚀
