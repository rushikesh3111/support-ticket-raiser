# 🎫 Support Ticket Raiser — SDLC Project Plan (Monolithic Architecture)

**Backend Framework:** FastAPI (Python) — a single, well-modularized monolithic application (not microservices).

**Scale Target:** Small support desk — **10–20 concurrent support agents/customers**, not enterprise-wide thousands of users. Architecture is deliberately kept simple and low-ops for this scale, while remaining modular enough to split into services later if usage grows.

This plan follows the standard **Software Development Life Cycle (SDLC)**: Requirement Analysis → Feasibility Study → System Design → Implementation → Integration & API Testing → Deployment → Maintenance.

---

## 1. Requirement Analysis

### 1.1 Objective
Build an enterprise-grade support ticket raising and tracking system that lets employees/customers log issues, tracks them through resolution, enforces SLAs, and gives management visibility via reporting.

### 1.2 Stakeholders
- End Users (ticket raisers)
- Support Agents / IT Team
- Team Leads / Managers
- System Administrators
- Compliance & Security Officers

### 1.3 Functional Requirements
| ID | Requirement |
|---|---|
| FR-1 | Users can create tickets with title, description, category, priority, and attachments |
| FR-2 | Tickets can be assigned automatically (round-robin/rules) or manually |
| FR-3 | Ticket status lifecycle: `Open → In Progress → On Hold → Resolved → Closed` |
| FR-4 | Comment/conversation thread per ticket |
| FR-5 | SLA policies per priority level with breach detection |
| FR-6 | Notifications via Email / In-app / Slack-Teams webhook |
| FR-7 | Role-based dashboards (User, Agent, Admin) |
| FR-8 | Full audit trail of every ticket action |
| FR-9 | Search and filter tickets (status, priority, category, assignee, date range) |
| FR-10 | Reporting: ticket volume, resolution time, SLA compliance, CSAT |

### 1.4 Non-Functional Requirements
| Category | Target |
|---|---|
| Scalability | Support 10–20 concurrent users comfortably; single-instance deployment with room to add 1–2 more Uvicorn workers if needed |
| Availability | 99.5% uptime (small-desk target, not enterprise HA) |
| Performance | API p95 response time < 500ms |
| Security | RBAC, encryption at rest & in transit, SSO (OAuth2) optional at this scale |
| Compliance | GDPR-aware data handling (retention, right-to-erasure) |
| Maintainability | Modular monolith — clean internal module boundaries, >80% test coverage per API |

### 1.5 Constraints
- Backend **must** be built exclusively on **FastAPI** — no Node.js/Java/Django alternatives permitted, including for auxiliary logic (notifications, SLA checks, reporting), which live as internal modules/background tasks within the same FastAPI application (using Celery/APScheduler for async jobs — not separate frameworks or separate deployable services).
- Architecture is **monolithic by design** at this scale (10–20 users): one codebase, one deployable unit, one primary database. This avoids the operational overhead of microservices (service discovery, distributed tracing, message brokers between services) that isn't justified at this user count.

---

## 2. Feasibility Study

| Type | Assessment |
|---|---|
| **Technical** | FastAPI + PostgreSQL + Redis + Celery is mature and well-suited for async I/O-heavy ticketing workloads. Async support in FastAPI handles concurrent notification/webhook calls efficiently. |
| **Operational** | Existing IT/support staff can adopt a modern web UI with minimal training; SSO reduces onboarding friction. |
| **Economic** | Open-source stack (FastAPI, PostgreSQL, Redis, React) minimizes licensing cost; cloud infra costs scale with usage. |
| **Schedule** | Estimated 24–28 weeks end-to-end (see Section 10). |

---

## 3. System Design

### 3.1 High-Level Architecture (Monolithic)

```
                 ┌─────────────────────────┐
                 │   Web / Mobile Clients   │
                 │   (React.js Frontend)    │
                 └────────────┬─────────────┘
                              │ HTTPS
                 ┌────────────▼─────────────┐
                 │   NGINX (reverse proxy)   │
                 └────────────┬─────────────┘
                              │
                 ┌────────────▼─────────────────────────────┐
                 │        Single FastAPI Application          │
                 │  ┌───────────┐ ┌───────────┐ ┌──────────┐ │
                 │  │  Ticket   │ │Notification│ │   SLA    │ │
                 │  │  Router   │ │  Router    │ │  Module  │ │
                 │  └───────────┘ └───────────┘ └──────────┘ │
                 │  ┌───────────┐ ┌───────────┐ ┌──────────┐ │
                 │  │ Comments  │ │Attachments │ │ Reports  │ │
                 │  │  Router   │ │  Router    │ │  Router  │ │
                 │  └───────────┘ └───────────┘ └──────────┘ │
                 │        (Uvicorn/Gunicorn, 2–4 workers)      │
                 └────────────┬─────────────────────────────┘
                              │
                 ┌────────────▼─────────────┐
                 │  Celery (in-process or    │
                 │  lightweight worker) +    │
                 │  Redis — SLA cron jobs,   │
                 │  async email dispatch     │
                 └────────────┬─────────────┘
                              │
        ┌─────────────────────▼─────────────────────┐
        │                Data Layer                    │
        │  PostgreSQL (single DB, all tables)          │
        │  Local disk / single S3 bucket (attachments) │
        │  Redis (cache + queue)                       │
        └───────────────────────────────────────────────┘
```

This is a **single FastAPI codebase and single deployable unit**. Tickets, Notifications, SLA, Comments, Attachments, and Reports are internal routers/modules sharing one database connection pool — not separate services. This is appropriate for a 10–20 user support desk: no service-to-service network calls, no distributed transactions, and much simpler local development, debugging, and deployment.

> **Note on future growth:** Because each module is cleanly separated (own router, own service-layer, own Pydantic schemas), this "modular monolith" can be split into microservices later if usage grows well beyond this scale — but that split is **not part of this plan**.

### 3.2 Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | **FastAPI** (Python 3.12), Uvicorn/Gunicorn (ASGI workers) |
| **Validation/Schemas** | Pydantic v2 |
| **ORM** | SQLAlchemy 2.0 (async) + Alembic (migrations) |
| **Task Queue** | Celery (single worker) + Redis broker — for SLA checks and async email; APScheduler is a lighter alternative at this scale |
| **Database** | PostgreSQL (single instance, all tables); local disk or single S3 bucket for attachments |
| **Cache** | Redis (optional at this scale, useful for session/rate-limit state) |
| **Search** | Postgres full-text search (`tsvector`) — Elasticsearch is unnecessary overhead for 10–20 users |
| **Auth** | JWT-based auth via FastAPI's `OAuth2PasswordBearer`; SSO (OAuth2) optional, add only if the org already has an IdP |
| **Frontend** | React.js + TypeScript + Tailwind CSS |
| **Realtime** | FastAPI native WebSocket support for live ticket updates |
| **Cloud** | Single VM or small managed container (AWS ECS/App Runner, Azure App Service, or a single Docker Compose host) — no Kubernetes needed at this scale |
| **Containerization** | Docker + Docker Compose (Kubernetes is optional, only if the org already standardizes on it) |
| **Monitoring** | Sentry for error tracking, basic Uvicorn/Gunicorn access logs; Prometheus/Grafana optional |

### 3.3 Database Schema (Core Entities)

```
users            → id, name, email, hashed_password, role, department, sso_id
tickets          → id, title, description, status, priority, category,
                   created_by (FK users), assigned_to (FK users),
                   created_at, updated_at, resolved_at
attachments      → id, ticket_id (FK), file_url, uploaded_by, uploaded_at
comments         → id, ticket_id (FK), author_id (FK), message, created_at
audit_logs       → id, ticket_id (FK), action, performed_by, timestamp, metadata (JSONB)
sla_policies     → id, priority, response_time_mins, resolution_time_mins
notifications    → id, user_id (FK), ticket_id (FK), channel, status, sent_at
kb_articles      → id, title, content, tags, linked_category
```

### 3.4 FastAPI Project Structure

```
ticket-system/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── core/
│   │   ├── config.py           # Settings via pydantic-settings
│   │   ├── security.py         # JWT, OAuth2, password hashing
│   │   └── logging.py
│   ├── api/
│   │   └── v1/
│   │       ├── routers/
│   │       │   ├── tickets.py
│   │       │   ├── users.py
│   │       │   ├── comments.py
│   │       │   ├── attachments.py
│   │       │   ├── sla.py
│   │       │   └── reports.py
│   │       └── deps.py         # Dependency injection (DB session, auth)
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/                # Business logic layer
│   ├── workers/                # Celery tasks (SLA checks, notifications)
│   ├── db/
│   │   ├── session.py
│   │   └── migrations/         # Alembic
│   └── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── alembic.ini
```

### 3.5 Core API Endpoints (FastAPI)

```
POST   /api/v1/auth/login                  → OAuth2/JWT login
POST   /api/v1/tickets/                    → Create ticket
GET    /api/v1/tickets/                    → List tickets (filters, pagination)
GET    /api/v1/tickets/{ticket_id}         → Get ticket detail
PUT    /api/v1/tickets/{ticket_id}         → Update ticket
DELETE /api/v1/tickets/{ticket_id}         → Archive ticket
POST   /api/v1/tickets/{ticket_id}/comments     → Add comment
GET    /api/v1/tickets/{ticket_id}/history      → Audit trail
POST   /api/v1/tickets/{ticket_id}/attachments  → Upload attachment
GET    /api/v1/reports/sla-compliance      → SLA report
GET    /api/v1/reports/agent-performance   → Agent performance metrics
WS     /ws/tickets/{ticket_id}             → Real-time ticket updates
```

Each router uses FastAPI's `Depends()` for auth, DB session injection, and RBAC checks; Pydantic schemas enforce strict request/response validation and auto-generate OpenAPI/Swagger docs at `/docs`.

---

## 4. Implementation Plan (Development Phase)

### 4.1 Backend (FastAPI) Modules — all within the single application

1. **Auth Module** — JWT issuance/validation, RBAC dependency guards (SSO added only if required)
2. **Ticket Module** — CRUD, status transitions, assignment logic
3. **Comment Module** — threaded conversation per ticket
4. **Attachment Module** — file upload to local disk/S3 with basic virus scan hook
5. **SLA Module** — Celery/APScheduler job checking ticket age vs `sla_policies`, running in-process
6. **Notification Module** — async dispatch to Email (SES/SendGrid), optional Slack/Teams webhook, in-app via WebSocket
7. **Reporting Module** — aggregation queries exposed as REST endpoints, feeding a lightweight dashboard
8. **Audit Module** — middleware/event hooks that log every state-changing action

All eight modules live as routers/services inside **one FastAPI app** (see structure in Section 3.4) — none are separate deployables.

### 4.2 Frontend Modules
- Dashboard (open tickets, SLA status widgets)
- Ticket creation form (rich text, drag-drop attachments, KB auto-suggest)
- Ticket list (filterable/sortable, status badges)
- Ticket detail (thread view, real-time updates via WebSocket)
- Admin panel (users, SLA policies, categories)
- Reports (charts via Recharts/Chart.js)

### 4.3 Integrations
| Integration | Purpose |
|---|---|
| Active Directory / LDAP | Enterprise authentication |
| Slack / MS Teams | Notifications in chat |
| JIRA / Azure DevOps | Escalate bugs to dev backlog |
| Email-to-Ticket parser | Auto-create tickets from inbound email (FastAPI background task) |
| PagerDuty / Datadog | Auto-create tickets from monitoring alerts |
| Confluence KB | Suggest articles during ticket creation |

---

## 5. Security & Compliance

- TLS 1.2+ in transit, AES-256 at rest
- Password hashing via `passlib` (bcrypt) inside FastAPI security module
- RBAC enforced via FastAPI dependency injection on every route
- Rate limiting via `slowapi` (FastAPI middleware)
- Input validation via Pydantic (mitigates injection risks)
- Immutable audit logs, PII masking in logs/reports
- GDPR: data retention policy, right-to-erasure endpoint
- Penetration testing prior to go-live (OWASP Top 10 checklist)

---

## 6. Testing Strategy (Per-API, Integrated into SDLC)

Testing is not a single late-stage phase here — each API is tested as soon as it's built, before the next module starts. This keeps defects cheap to fix and matches the small team's iteration speed.

### 6.1 Testing Approach by SDLC Stage

| SDLC Stage | Testing Activity |
|---|---|
| Design | Define test cases and expected request/response schemas alongside the OpenAPI contract for each endpoint, before coding starts |
| Implementation | Write unit tests **in the same PR** as the endpoint (TDD-lite: at minimum, tests land with the code, not after) |
| Post-Implementation | Run integration tests against a real (test) DB for that module before merging |
| Pre-Release (per sprint) | Run full regression suite + manual exploratory testing on staging |
| Pre-Go-Live | End-to-end + load test against the 10–20 user target, then security scan |
| Post-Go-Live | Regression suite re-run manually before every future release |

### 6.2 Per-API Test Matrix

Every endpoint below gets its own test cases before being marked "done" — this is the working checklist for backend developers.

| API Endpoint | Test Cases to Cover |
|---|---|
| `POST /auth/login` | Valid credentials → token issued; invalid password → 401; locked/inactive user → 403; malformed payload → 422 |
| `POST /tickets/` | Valid ticket → 201 + correct schema; missing required field → 422; unauthenticated → 401; oversized attachment → rejected |
| `GET /tickets/` | Pagination correctness; filter by status/priority/category; empty result set; unauthorized role sees only permitted tickets |
| `GET /tickets/{id}` | Existing ticket → 200; non-existent id → 404; ticket belonging to another user (non-agent) → 403 |
| `PUT /tickets/{id}` | Valid status transition (e.g., Open→In Progress) → 200; invalid transition (e.g., Closed→Open) → 400; unauthorized role → 403; concurrent update conflict handled |
| `DELETE /tickets/{id}` | Soft-delete/archive success → 200; already-archived ticket → 409/400; non-admin attempt → 403 |
| `POST /tickets/{id}/comments` | Comment added → 201; empty message → 422; comment on closed ticket → business-rule check (allowed/blocked as designed) |
| `GET /tickets/{id}/history` | Returns chronological audit entries; empty history for new ticket; unauthorized access → 403 |
| `POST /tickets/{id}/attachments` | Valid file type/size → 201; disallowed file type → 400; file exceeds size limit → 413 |
| `GET /reports/sla-compliance` | Correct % calculation against seeded test data; no data → graceful empty response, not 500 |
| `GET /reports/agent-performance` | Correct aggregation per agent; date-range filter accuracy |
| SLA background job | Simulate ticket past SLA threshold → breach flagged + notification triggered; ticket within SLA → no false breach |
| `WS /ws/tickets/{id}` | Client receives update on status change; connection drop/reconnect handled; unauthorized client rejected |

### 6.3 Testing Tools

| Test Type | Tools |
|---|---|
| Unit Testing (per API) | `pytest`, `pytest-asyncio`, FastAPI `TestClient` — one test module per router |
| Integration Testing | `httpx.AsyncClient` against a test PostgreSQL DB (via `pytest` fixtures + Alembic test migrations) |
| Contract Testing | Auto-generated OpenAPI schema (FastAPI `/openapi.json`) validated against the design-stage contract for each endpoint |
| End-to-End Testing | Postman/Newman collection covering full user journeys (raise → assign → resolve → close) |
| Load & Performance | Locust/k6 — scaled to a **realistic 10–20 concurrent user load**, not enterprise-scale simulation |
| Security Testing | Bandit (Python SAST), manual auth/RBAC bypass checks per endpoint |
| Accessibility (frontend) | Axe, Lighthouse |

### 6.4 Coverage & Release Checklist

- Every new endpoint requires unit + integration tests **before it's considered done** — checked manually against the per-API matrix above, not via an automated pipeline.
- Target: **>80% coverage per module**, checked via `pytest --cov` run locally/manually before each release, tracked per API router so no single endpoint hides behind an aggregate number.
- A release is not shipped if any per-API test in the matrix above is missing, skipped, or failing.

---

## 7. Deployment

Delivery is manual/direct — the project's scope is to ship two runnable applications, not to stand up a CI/CD pipeline:

- **Backend deliverable:** a single FastAPI application (Dockerized), runnable via `uvicorn app.main:app` or `docker compose up`, with `requirements.txt`, `.env.example`, and Alembic migrations included so it can be started on any server or local machine.
- **Frontend deliverable:** a React build (`npm run build`) producing static assets, deployable to any static host or served via the same server as the API.
- Tests (Section 6) are run manually by the QA engineer/developer before each release — `pytest` for backend, component tests for frontend — rather than gated by an automated pipeline.

### 7.1 Infrastructure
- Single Dockerized FastAPI app behind Gunicorn+Uvicorn workers (2–4 workers is sufficient for 10–20 users)
- Docker Compose on one VM, or a single small managed container service (ECS/App Runner/App Service) — Kubernetes not required at this scale
- Managed PostgreSQL (RDS/Cloud SQL, smallest tier), Redis optional
- Sentry for error tracking; basic access/app logs sufficient at this scale
- Manual DB backups (or a simple scheduled cron job) with point-in-time recovery

---

## 8. Maintenance & Support (Post Go-Live)

- 24/7 monitoring with alerting (Prometheus Alertmanager → PagerDuty)
- Monthly dependency/security patching (FastAPI, SQLAlchemy, Pydantic version upgrades)
- Quarterly SLA policy review
- Continuous backlog grooming for feature requests (KB expansion, additional integrations)
- Incident postmortems logged and fed back into the audit/reporting module

---

## 9. Reporting & Analytics (KPIs Delivered)

- Agent performance: tickets resolved, avg response/resolution time
- Ticket volume trends & peak-period analysis
- SLA compliance percentage
- Category/issue-type breakdown
- CSAT scores from post-resolution surveys

---

## 10. Recommended Team Structure (Right-Sized for 10–20 Users)

| Role | Count |
|---|---|
| Product Owner / PM | 1 (part-time) |
| FastAPI Backend Developer | 2 |
| Frontend Developer (React) | 1 |
| QA Engineer (owns per-API test matrix) | 1 |
| DevOps (part-time, single-environment setup) | 1 (shared/part-time) |

This is a lean team appropriate for a single-monolith, small-user-base build — no dedicated solution architect, security specialist, or multiple QA engineers required at this scale, though a security review pass before go-live is still recommended.

---

## 11. Success Metrics (KPIs)

- 🎯 Ticket resolution time reduced by 30%
- 🎯 SLA compliance rate > 95%
- 🎯 User adoption rate > 85% within 3 months
- 🎯 System uptime > 99.5%
- 🎯 CSAT score > 4/5
- 🎯 Backend test coverage > 80%, tracked per API endpoint

---

## 12. MVP Recommendation

Start with an MVP restricted to:
- Ticket creation, listing, and detail view (FastAPI CRUD + React UI)
- Manual assignment and status tracking
- Email notifications (Celery + SES/SendGrid)
- Basic RBAC (User/Agent/Admin)

Then iterate with SLA automation, analytics dashboards, third-party integrations, and knowledge-base suggestions in subsequent sprints.
