# Django Serverless Blog

A fully serverless blog API built with Django REST Framework, deployed to AWS using Terraform. Vue 3 frontend served via CloudFront.

## Architecture

```
User → CloudFront → /api/*  → Lambda (Django + Mangum) → RDS (PostgreSQL)
                  → /*      → S3 (Vue 3 SPA)
```

### Backend — Service → Repository → Interface Pattern

```
blog/
├── interfaces/
│   └── base_repository_interface.py   # Abstract base class (ABC) with Generic[T]
├── repositories/
│   ├── base_repository.py             # Concrete ORM implementation with dynamic filtering
│   └── post_repository.py             # Post-specific repository
├── models/
│   └── post.py                        # Django model — no business logic
├── services/
│   └── post_service.py                # All business logic lives here
├── serializers/
│   └── post_serializer.py             # DRF serializer for validation/output
├── views/
│   └── post_view.py                   # Thin ViewSet — delegates to service
└── tests/
    └── test_post_service.py           # Unit tests with mock repository
```

**Why this pattern?**

- **Models** stay clean — no business logic, just data structure
- **Repositories** handle all database access — easy to swap ORMs or mock for testing
- **Services** contain business logic — testable without hitting the database
- **Views** are thin — just handle HTTP, delegate everything to the service
- **Interface** allows dependency injection — the service depends on an abstraction, not a concrete implementation

### Frontend — Vue 3 + TypeScript + Tailwind

```
frontend/src/
├── pages/posts/          # Page components per resource
├── services/posts/       # API calls per resource
├── types/                # TypeScript interfaces
├── router/               # Vue Router config
└── App.vue               # Root layout
```

### Infrastructure — Terraform (AWS)

```
infra/
├── providers.tf          # AWS provider config
├── variables.tf          # Input variables (region, DB creds, secrets)
├── network.tf            # VPC, subnets, NAT gateway, security groups
├── database.tf           # RDS PostgreSQL
├── lambda.tf             # Lambda function + IAM + function URL
├── frontend.tf           # S3 bucket + CloudFront CDN
└── outputs.tf            # Deployed URLs and endpoints
```

### CI/CD — GitHub Actions

- **Pull requests** → runs backend tests (pytest + Postgres) and frontend checks (TypeScript + build)
- **Merge to main** → runs tests, then deploys infrastructure via Terraform, builds and uploads frontend to S3, invalidates CloudFront cache

## Tech Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| API            | Django 6, Django REST Framework     |
| ASGI Adapter   | Mangum (Lambda compatibility)       |
| Database       | PostgreSQL 16 (Docker / RDS)        |
| Frontend       | Vue 3, Vite, TypeScript, Tailwind   |
| Infrastructure | Terraform, AWS (Lambda, S3, CloudFront, RDS, VPC) |
| CI/CD          | GitHub Actions                      |
| Local Dev      | Docker Compose (Django + Postgres)  |
| Testing        | pytest, pytest-django               |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 22+
- AWS CLI (for deployment)
- Terraform (for deployment)

### Local Development

```bash
# Start Django + Postgres
docker compose up --build

# Run migrations
docker compose exec django python manage.py migrate

# Seed sample data
docker compose exec django python manage.py seed_posts

# Create a superuser for admin access
docker compose exec django python manage.py createsuperuser

# Start the Vue frontend (in a separate terminal)
cd frontend && npm install && npm run dev
```

### Endpoints

| URL                              | Description           |
|----------------------------------|-----------------------|
| http://localhost:5173             | Vue frontend          |
| http://localhost:8000/api/posts/  | Posts API             |
| http://localhost:8000/admin/      | Django admin panel    |

### API Authentication

- **GET** requests are public
- **POST / PUT / DELETE** require superuser credentials (Basic Auth)

### Running Tests

```bash
# Backend (via Docker)
docker compose exec django python -m pytest -v

# Frontend
cd frontend && npx vue-tsc --noEmit
```

## Deployment

### First-Time Setup

```bash
# Configure AWS CLI
aws configure

# Create terraform.tfvars from the example
cp infra/terraform.tfvars.example infra/terraform.tfvars
# Edit terraform.tfvars with your secrets

# Package Lambda
bash scripts/package_lambda.sh

# Deploy infrastructure
cd infra
terraform init
terraform plan
terraform apply

# Run migrations on RDS (via Lambda)
aws lambda invoke --function-name django-serverless-blog-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"manage":"migrate"}' \
  --region eu-west-2 /tmp/migrate-out.json

# Seed data (optional)
aws lambda invoke --function-name django-serverless-blog-api \
  --cli-binary-format raw-in-base64-out \
  --payload '{"manage":"seed_posts"}' \
  --region eu-west-2 /tmp/seed-out.json

# Build and deploy frontend to S3
cd ../frontend && npm run build
aws s3 sync dist s3://django-serverless-blog-frontend --delete
```

### Redeploying After Code Changes

```bash
# Rebuild Lambda package and deploy
cd ~/Sites/django-serverless-blog
bash scripts/package_lambda.sh
cd infra && terraform apply
```

### GitHub Actions Secrets

Add these in repo Settings → Secrets and variables → Actions:

| Secret               | Description                    |
|----------------------|--------------------------------|
| `AWS_ACCESS_KEY_ID`  | IAM user access key            |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key         |
| `DB_PASSWORD`        | RDS PostgreSQL password        |
| `DJANGO_SECRET_KEY`  | Django secret key              |
