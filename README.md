# ApexBank: Secure Django + MySQL Deployment on AWS

A small banking web application deployed on AWS as a hands on **cloud and DevOps** project. Users can create accounts, send and withdraw money, and an admin can deposit money. The focus of this repository is **how the app is deployed, secured and operated**, not the app's business logic.

> **Honest note:** the application code (Django backend and HTML/CSS/JavaScript frontend) was **vibe coded**, meaning it was built with AI assistance. The part I designed, built, debugged and documented myself is the **AWS infrastructure, security, CI/CD pipeline and deployment runbook** around it.

| | |
|---|---|
| 🎥 **Demo video** | [link](https://lnkd.in/p/dByfhUkg) |
| 💼 **LinkedIn post** | [[link](https://lnkd.in/p/dByfhUkg)] |

> **Live demo status:** The site is **not kept running** to avoid AWS costs. I build the stack, test it, record it, and tear everything down. Please see the demo video.

---

## Architecture

**How a request flows:** User → Route 53 → Application Load Balancer (HTTPS, public subnets) → EC2 server running Docker (private subnet) → RDS MySQL (private subnets, no internet route). The server reaches the internet only outbound, through a NAT Gateway.

---

## What the app does

- **Sign-up** with name, email, phone, PAN and Aadhaar. (Only **fake data** is used in this project.)
- **Login** with email or username.
- **Send and withdraw money** from an account.
- **Admin only deposits** into any account.
- Two admin interfaces: the built-in **Django admin** and a **custom admin panel**.

---

## Tech stack

| Area | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Django, Gunicorn |
| Static files | WhiteNoise (served from the container, no Nginx or S3 needed) |
| Database | MySQL 8.4 on Amazon RDS |
| Containers | Docker (multi-stage build, non-root user) |
| CI/CD | GitHub Actions with OIDC |
| AWS networking | VPC, subnets, route tables, Internet Gateway, NAT Gateway, S3 gateway endpoint, security groups |
| AWS compute and edge | EC2 Auto Scaling group, Application Load Balancer, Route 53, ACM |
| AWS security and ops | IAM roles, SSM Session Manager, SSM Parameter Store, ECR (with image scanning) |

---

## How the code is organised

```
ApexBank/
├── .github/
│   └── workflows/
│       ├── deploy.yml            # CI/CD: build, test, push, migrate & deploy
│       └── oidc-debug.yml        # GitHub Actions OIDC workflow / debugging
├── accounts/                     # User authentication & account management app
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── banking_project/              # Core Django project package
│   ├── __init__.py
│   ├── middleware.py             # HealthCheck / custom middleware
│   ├── settings.py               # Environment-based configuration
│   ├── urls.py                   # Root URL routing
│   └── wsgi.py
├── transactions/                 # Core banking & transfer logic app
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/                       # Source static files (CSS & JavaScript)
│   ├── css/
│   │   ├── dashboard.css
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── validation.js
├── templates/                    # HTML templates
│   ├── accounts/                 # login, register, profile
│   ├── admin_portal/             # admin dashboard, deposits, details
│   ├── transactions/             # transaction history, transfer forms
│   └── base.html                 # Base layout template
├── .dockerignore
├── .env.example                  # Template for environment variables
├── .gitignore
├── db_setup.sql                  # Initial database setup script
├── docker-compose.yml            # Local multi-container development setup
├── Dockerfile                    # Container build: Gunicorn + WhiteNoise
├── manage.py
├── README.md
├── requirements.txt              # Project dependencies
└── run_migrations.py             # Migration runner script
```

---

## Security highlights

- **Account security:** root user with MFA and **no access keys**; daily work through a separate IAM admin user with MFA and **no access keys**.
- **No SSH, no key pair:** The server is reached through **SSM Session Manager**.
- **No stored AWS credentials:** GitHub Actions authenticates with **OIDC** and receives temporary credentials. The IAM trust policy accepts only this repository on the `main` branch.
- **Least-privilege IAM roles:** The server can pull one ECR repository and read one Parameter Store path.
- **Secrets** live in encrypted **SSM Parameter Store**, never in the repo or in GitHub.
- **Network:** public load balancer only; The server and database are in private subnets; security groups are chained ALB → server → database.
- **Data:** RDS is private, encrypted, and not publicly accessible. Three database identities: an admin for emergencies, a migration user that can change tables, and an app user that can only read and write rows.
- **Hardening:** IMDSv2 only, encrypted disks, immutable ECR image tags with scan on push.

---

## CI/CD pipeline

On every push to `main`, GitHub Actions runs:

1. **Test:** Django checks and tests against a temporary MySQL.
2. **Build:** builds the Docker image and pushes it to ECR, tagged with the commit hash.
3. **Migrate:** runs database migrations once, using the migration-only database user, through SSM Run Command.
4. **Replace:** the Auto Scaling group starts a new server, waits until the load balancer reports it healthy, then removes the old one (rolling replacement).

---

## Deploying it yourself

**Environment variables the container expects**

| Variable | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (required) |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated origins, e.g. `https://example.com` (no trailing slash) |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | Database connection |
| `SECURE_SSL_REDIRECT` | Set to `false` for local HTTP testing |

**Quick container check (no database needed for the health route)**

```bash
docker build -t apexbank:test .
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY=local-test -e ALLOWED_HOSTS=localhost \
  -e SECURE_SSL_REDIRECT=false apexbank:test
curl -i http://localhost:8000/health/    # expect 200 and "ok"
```

---

## Cost

Roughly **$0.11 per hour** while the stack is running and **$2.70 per day**, **$80 per month if left running**. A full build, record and teardown session cost about **$1.07** (Nearly 10 times whole infrastructure created and teardown while learning), checked in Cost Explorer. Everything is deleted afterwards using a teardown checklist.

---

## Lessons learned (real problems I hit)

- A route table must be **associated** with its subnets. Mine were not, so the server had no route out and my Auto Scaling group replaced it in a loop.
- GitHub's OIDC token subject now includes **owner and repository IDs** for newer repositories, so the IAM trust policy must match exactly.
- AWS **tag values are case sensitive** (`ApexBank` is not `apexbank`), and the pipeline found the server by tag.
- "Re-run failed jobs" does not rebuild a missing image after the registry is recreated; start a fresh run.

---

## Limitations and next steps

- Single application server and single-instance database (cost); no WAF yet, CloudWatch alarms not set up.
- The application itself is AI-generated and has not had a security review. **Do not use real personal data (PAN, Aadhaar) or real money.**
- This project is just production ready not suitable for real production. But I learned a lot new concpets while working on this project. This is **Stage 1**, I'm gone to work on this project more.

---

## Author

**Sreeram Manjnath Reddy** · LinkedIn Profile Link: (https://www.linkedin.com/in/manjunath139/)
