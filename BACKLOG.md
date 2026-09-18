# BACKLOG - Support Ticket Raiser System

**Specification:** `final_support_tic.md`  
**Architecture:** Monolithic FastAPI (Python 3.12) + React (TypeScript + Tailwind CSS) + SQLite/PostgreSQL  
**Repository:** `rushikesh3111/support-ticket-raiser`  
**Branch:** `feature/support-ticket-raiser-mvp`  

---

##  Sprint & Module Backlog

### Phase 1: Foundation, Backlog & Architecture
- [x] **TASK-01**: Initialize Git repository, configure remotes, create feature branch `feature/support-ticket-raiser-mvp`, setup `BACKLOG.md`.
- [ ] **TASK-02**: Setup project layout (`app/`, `frontend/`, `docs/`, `.github/workflows/`, `tests/`), configure dependencies (`pyproject.toml` / `requirements.txt`).

### Phase 2: Core Data Models & Database Layer
- [ ] **TASK-03**: Implement SQLAlchemy models: `User`, `Ticket`, `Comment`, `Attachment`, `AuditLog`, `SLAPolicy`, `Notification`, `KBArticle`.
- [ ] **TASK-04**: Database engine, session management, async/sync SQLite fallback & PostgreSQL support, initial seed data (default admin, agent, users, SLA tiers).

### Phase 3: Authentication & RBAC Module
- [ ] **TASK-05**: Auth service & endpoints:
  - `POST /api/v1/auth/login` (OAuth2 JWT token generation)
  - `POST /api/v1/auth/register` (User registration with role enforcement)
  - `GET /api/v1/auth/me` (Current user profile & RBAC check)
  - Role-based dependencies: `get_current_user`, `require_role(["admin", "agent", "user"])`

### Phase 4: Ticket Management Module
- [ ] **TASK-06**: Tickets service & endpoints:
  - `POST /api/v1/tickets/` (Ticket creation with category, priority, validation)
  - `GET /api/v1/tickets/` (List tickets with status/priority/category/assignee filters, pagination, search)
  - `GET /api/v1/tickets/{ticket_id}` (Ticket detail with RBAC ownership checks)
  - `PUT /api/v1/tickets/{ticket_id}` (Status transitions: Open -> In Progress -> On Hold -> Resolved -> Closed, assignment)
  - `DELETE /api/v1/tickets/{ticket_id}` (Soft-delete/archive ticket, admin-only guard)

### Phase 5: Comments & Conversation Module
- [ ] **TASK-07**: Comments service & endpoints:
  - `POST /api/v1/tickets/{ticket_id}/comments` (Add threaded comments, internal agent notes, validation)
  - `GET /api/v1/tickets/{ticket_id}/comments` (List conversation history)

### Phase 6: Attachments Module
- [ ] **TASK-08**: Attachments service & endpoints:
  - `POST /api/v1/tickets/{ticket_id}/attachments` (Upload attachments, mime-type validation, size limits)
  - `GET /api/v1/tickets/{ticket_id}/attachments` (List attachments)
  - `GET /api/v1/attachments/{attachment_id}/download` (Download attachment file)

### Phase 7: SLA Module & Background Enforcement
- [ ] **TASK-09**: SLA policy CRUD & Breach Detection:
  - `GET /api/v1/sla/policies` & `POST /api/v1/sla/policies` (SLA policies management)
  - SLA computation engine (calculating response breach & resolution breach)
  - Background task / cron trigger for SLA monitoring

### Phase 8: Notification & Realtime Module
- [ ] **TASK-10**: In-app notifications & WebSockets:
  - `GET /api/v1/notifications/` (List unread/read notifications for user)
  - `PUT /api/v1/notifications/{id}/read` (Mark notification as read)
  - `WS /ws/tickets/{ticket_id}` (Real-time live ticket updates)

### Phase 9: Reporting & Audit Modules
- [ ] **TASK-11**: Reporting & Metrics:
  - `GET /api/v1/reports/sla-compliance` (SLA breach percentage & compliance rate)
  - `GET /api/v1/reports/agent-performance` (Agent resolution count, avg handling time)
  - `GET /api/v1/reports/ticket-volume` (Volume trends by status/category/priority)
- [ ] **TASK-12**: Audit Trail:
  - `GET /api/v1/tickets/{ticket_id}/history` (Chronological audit history of changes)

### Phase 10: 10-Tier Testing Suite (≥10 Tests per Endpoint)
- [ ] **TASK-13**: Implement comprehensive pytest suite with at least 10 robust test cases for every API endpoint (Auth, Tickets, Comments, Attachments, SLA, Reports, Audit, Notifications). Verify 100% pass rate.

### Phase 11: Modern React Frontend
- [ ] **TASK-14**: Full-featured responsive UI:
  - Authentication (Login, Register, Role switching)
  - Role-based Dashboards (Customer view, Support Agent view, Admin view)
  - Ticket Creation modal/page with rich inputs
  - Ticket Detail view with live updates, comments feed, file attachment uploads, status transition buttons, SLA countdown/breach badges
  - SLA Policies & Admin Panel
  - Analytics & Reports charts/tables (CSAT, SLA compliance, Agent leaderboard)
  - Real-time notification drawer

### Phase 12: Architecture Documentation (HLD, LLD, TESTING)
- [ ] **TASK-15**: Generate comprehensive `docs/HLD.md`, `docs/LLD.md`, and `docs/TESTING.md` according to AGENTS.md rules.

### Phase 13: CI/CD, Containerization & Production Deployment
- [ ] **TASK-16**: Setup GitHub Actions workflow `.github/workflows/ci.yml` (Lint, Test, Build).
- [ ] **TASK-17**: Create GitHub repository `rushikesh3111/support-ticket-raiser`, push branch, deploy backend + frontend with live URLs and verify post-deployment smoke tests.
