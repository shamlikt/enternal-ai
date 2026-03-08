# Enternal Health — Customer Deployment Guide

> Version: 1.0 | Updated: 2026-03-08

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|-----------------|-------|
| Docker Engine | 24.x | [Install guide](https://docs.docker.com/engine/install/) |
| Docker Compose plugin | v2.20+ | Bundled with Docker Desktop |
| CPU | 4 cores | 8 recommended for production |
| RAM | 8 GB | 16 GB recommended |
| Disk | 50 GB | For PostgreSQL data + Docker images |
| OS | Linux (Ubuntu 22.04+ / RHEL 8+) | macOS supported for dev only |

---

## Quick Start (Development)

```bash
# 1. Clone the repository
git clone <your-gitlab-repo-url> enternal
cd enternal

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env — at minimum set POSTGRES_PASSWORD and JWT_SECRET_KEY

# 3. Start all services
docker compose up --build

# 4. Access the platform
#    Frontend:  http://localhost:3000
#    Backend:   http://localhost:8000
#    API docs:  http://localhost:8000/docs
```

Default admin credentials (change immediately after first login):
- **Email:** admin@enternal.health
- **Password:** changeme

---

## Production Deployment

### Step 1: Prepare the server

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### Step 2: Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set **all** of the following:

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `enternal` |
| `POSTGRES_USER` | Database user | `enternal_user` |
| `POSTGRES_PASSWORD` | **Strong** database password | (generate with `openssl rand -base64 32`) |
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | (generate with `openssl rand -base64 48`) |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS IAM key with Bedrock access | (from customer AWS account) |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret | (from customer AWS account) |
| `CI_REGISTRY_IMAGE` | GitLab registry path | `registry.gitlab.com/org/enternal` |
| `IMAGE_TAG` | Docker image tag to deploy | `abc1234` (commit SHA) or `latest` |

Generate secrets:
```bash
openssl rand -base64 32   # for POSTGRES_PASSWORD
openssl rand -base64 48   # for JWT_SECRET_KEY
```

### Step 3: Pull and start production services

```bash
# Authenticate with GitLab Container Registry
docker login registry.gitlab.com

# Start with production overrides
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify all containers are healthy
docker compose ps
docker compose logs backend --tail=50
```

### Step 4: Configure TLS/HTTPS

**Required for HIPAA compliance.** The platform does not terminate TLS itself.
Place a reverse proxy in front of the `frontend` (port 3000) and `backend` (port 8000) containers.

#### Option A: Caddy (recommended — automatic HTTPS)

```bash
# Install Caddy
apt install caddy

# /etc/caddy/Caddyfile
your.domain.com {
    reverse_proxy localhost:3000
}

api.your.domain.com {
    reverse_proxy localhost:8000
}
```

#### Option B: nginx

```nginx
server {
    listen 443 ssl;
    server_name your.domain.com;

    ssl_certificate /etc/ssl/certs/enternal.crt;
    ssl_certificate_key /etc/ssl/private/enternal.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name api.your.domain.com;

    ssl_certificate /etc/ssl/certs/enternal.crt;
    ssl_certificate_key /etc/ssl/private/enternal.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Update the frontend environment to use HTTPS URLs:
```bash
# In .env
NEXT_PUBLIC_API_URL=https://api.your.domain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.your.domain.com/api/v1/agent/ws
```

---

## Environment Variable Reference

All variables are documented in `.env.example`. Key variables:

```bash
# PostgreSQL
POSTGRES_DB=enternal
POSTGRES_USER=enternal_user
POSTGRES_PASSWORD=<strong-password>

# JWT Authentication
JWT_SECRET_KEY=<min-32-char-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<iam-key>
AWS_SECRET_ACCESS_KEY=<iam-secret>
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Admin seeder (optional overrides)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@enternal.health
ADMIN_PASSWORD=<initial-password-change-immediately>

# Production image (docker-compose.prod.yml)
CI_REGISTRY_IMAGE=registry.gitlab.com/<org>/enternal
IMAGE_TAG=latest
```

---

## Backup and Restore

### Backup PostgreSQL

```bash
# Create backup
docker compose exec postgres pg_dump \
    -U ${POSTGRES_USER} ${POSTGRES_DB} \
    | gzip > enternal_$(date +%Y%m%d_%H%M%S).sql.gz

# Schedule daily backups (cron)
echo "0 2 * * * docker compose -f /opt/enternal/docker-compose.yml exec -T postgres pg_dump -U enternal_user enternal | gzip > /backups/enternal_\$(date +\%Y\%m\%d).sql.gz" | crontab -
```

### Restore PostgreSQL

```bash
# Stop the backend first
docker compose stop backend

# Restore
gunzip -c enternal_YYYYMMDD_HHMMSS.sql.gz | docker compose exec -T postgres \
    psql -U ${POSTGRES_USER} ${POSTGRES_DB}

# Restart
docker compose start backend
```

---

## Upgrade Procedure

```bash
# 1. Pull new images
docker compose -f docker-compose.yml -f docker-compose.prod.yml pull

# 2. Apply database migrations (runs automatically on backend startup)
#    Or run manually:
docker compose exec backend alembic upgrade head

# 3. Recreate containers with new images
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-build

# 4. Verify health
docker compose ps
curl -s http://localhost:8000/api/v1/health
```

---

## Troubleshooting

### Backend fails to start

```bash
# View logs
docker compose logs backend --tail=100

# Common causes:
# - DATABASE_URL incorrect — check POSTGRES_* vars match
# - Alembic migration failed — check DB connectivity
# - Missing JWT_SECRET_KEY
```

### Database connection refused

```bash
# Check postgres health
docker compose ps postgres
docker compose exec postgres pg_isready -U ${POSTGRES_USER}

# Check network
docker compose exec backend env | grep DATABASE_URL
```

### Frontend shows API errors

```bash
# Verify NEXT_PUBLIC_API_URL is reachable from the browser (not inside Docker)
# It must be the external hostname/IP, not 'backend' (internal Docker DNS)
curl http://localhost:8000/api/v1/health
```

### Reset to clean state (destructive)

```bash
# WARNING: This deletes ALL data.
docker compose down -v
docker compose up --build
```

---

## HIPAA Compliance Notes

- Enable TLS/HTTPS before any production use (see Step 4 above).
- Obtain a BAA with AWS before routing data through AWS Bedrock.
- Change the default admin password on first login.
- PostgreSQL data volume (`pgdata`) must be encrypted at rest — use OS-level
  encryption (e.g., LUKS on Linux, encrypted EBS on AWS).
- All API calls, logins, and data exports are written to the `audit_log` table.
  Retain audit logs per your organization's compliance requirements.
- PHI is never written to application logs (enforced by the PHI sanitizer in
  `app/core/logging.py`).
- Restrict SSH and Docker socket access to authorized administrators only.
