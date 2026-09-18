# BACKLOG - Support Ticket Raiser System

**Specification:** `final_support_tic.md`  
**Architecture:** Monolithic FastAPI (Python 3.12) + React (TypeScript + Tailwind CSS) + SQLite/PostgreSQL  
**Repository:** `rushikesh3111/support-ticket-raiser`  
**Branch:** `feature/support-ticket-raiser-mvp`  
**Live Frontend:** `http://10.0.32.214:3005`  
**Live Backend API:** `http://10.0.32.214:8085`  
**Swagger API Docs:** `http://10.0.32.214:8085/docs`  

---

## Sprint & Module Backlog

### Phase 1: Foundation, Backlog & Architecture
- [x] **TASK-01**: Initialize Git repository, configure remotes, create feature branch `feature/support-ticket-raiser-mvp`, setup `BACKLOG.md`.
- [x] **TASK-02**: Setup project layout (`app/`, `frontend/`, `docs/`, `.github/workflows/`, `tests/`), configure dependencies (`pyproject.toml` / `requirements.txt`).

### Phase 2: Core Data Models & Database Layer
- [x] **TASK-03**: Implement SQLAlchemy models: `User`, `Ticket`, `Comment`, `Attachment`, `AuditLog`, `SLAPolicy`, `Notification`, `KBArticle`.
- [x] **TASK-04**: Database engine, session management, SQLite & PostgreSQL support, initial seed data (default admin, agent, users, SLA tiers).

### Phase 3: Authentication & RBAC Module
- [x] **TASK-05**: Auth service & endpoints:
  - `POST /api/v1/auth/login` (OAuth2 JWT token generation)
  - `POST /api/v1/auth/login/json` (JSON payload login)
  - `POST /api/v1/auth/register` (User registration with role enforcement)
  - `GET /api/v1/auth/me` (Current user profile & RBAC check)
  - Role-based dependencies: `get_current_user`, `require_role(["admin", "agent", "user"])`

### Phase 4: Ticket Management Module
- [x] **TASK-06**: Tickets service & endpoints:
  - `POST /api/v1/tickets/` (Ticket creation with category, priority, validation)
  - `GET /api/v1/tickets/` (List tickets with status/priority/category/assignee filters, pagination, search)
  - `GET /api/v1/tickets/{ticket_id}` (Ticket detail with RBAC ownership checks)
  - `PUT /api/v1/tickets/{ticket_id}` (Status transitions: Open -> In Progress -> On Hold -> Resolved -> Closed, assignment)
  - `DELETE /api/v1/tickets/{ticket_id}` (Soft-delete/archive ticket, admin-only guard)

### Phase 5: Comments & Conversation Module
- [x] **TASK-07**: Comments service & endpoints:
  - `POST /api/v1/tickets/{ticket_id}/comments` (Add threaded comments, internal agent notes, validation)
  - `GET /api/v1/tickets/{ticket_id}/comments` (List conversation history)

### Phase 6: Attachments Module
- [x] **TASK-08**: Attachments service & endpoints:
  - `POST /api/v1/tickets/{ticket_id}/attachments` (Upload attachments, mime-type validation, size limits)
  - `GET /api/v1/tickets/{ticket_id}/attachments` (List attachments)
  - `GET /api/v1/attachments/{attachment_id}/download` (Download attachment file)

### Phase 7: SLA Module & Background Enforcement
- [x] **TASK-09**: SLA policy CRUD & Breach Detection:
  - `GET /api/v1/sla/policies` & `POST /api/v1/sla/policies` (SLA policies management)
  - SLA computation engine (calculating response breach & resolution breach)
  - Automated SLA check triggers & notifications

### Phase 8: Notification & Realtime Module
- [x] **TASK-10**: In-app notifications & WebSockets:
  - `GET /api/v1/notifications/` (List unread/read notifications for user)
  - `PUT /api/v1/notifications/{id}/read` (Mark notification as read)
  - `PUT /api/v1/notifications/read-all` (Mark all notifications as read)
  - `WS /ws/tickets/{ticket_id}` (Real-time live ticket updates)

### Phase 9: Reporting & Audit Modules
- [x] **TASK-11**: Reporting & Metrics:
  - `GET /api/v1/reports/sla-compliance` (SLA breach percentage & compliance rate)
  - `GET /api/v1/reports/agent-performance` (Agent resolution count, avg handling time)
  - `GET /api/v1/reports/ticket-volume` (Volume trends by status/category/priority)
- [x] **TASK-12**: Audit Trail:
  - `GET /api/v1/tickets/{ticket_id}/history` (Chronological audit history of changes)

### Phase 10: 10-Tier Testing Suite (≥10 Tests per Endpoint)
- [x] **TASK-13**: Implement comprehensive pytest suite with 165 automated tests (at least 10 robust test cases for every API endpoint: Auth, Tickets, Comments, Attachments, SLA, Reports, Audit, Notifications). Verified 100% pass rate.

### Phase 11: Modern React Frontend
- [x] **TASK-14**: Full-featured responsive UI:
  - Authentication Modal (Login, Register, 1-click Quick Demo logins)
  - Role-based views & guards (User, Support Agent, Admin)
  - Ticket Creation modal with rich inputs & attachments
  - Ticket Detail view with thread view, internal staff notes, file download links, status transition controls, SLA countdown monitor
  - Analytics & Reports charts/tables (SLA compliance, Agent leaderboard, Category distribution)
  - Real-time in-app notification drawer

### Phase 12: Architecture Documentation (HLD, LLD, TESTING)
- [x] **TASK-15**: Generated comprehensive `docs/HLD.md`, `docs/LLD.md`, and `docs/TESTING.md` according to AGENTS.md rules.

### Phase 13: CI/CD, Containerization & Production Deployment
- [x] **TASK-16**: Setup GitHub Actions workflow `.github/workflows/ci.yml` (Lint, Test, Build).
- [x] **TASK-17**: Created GitHub repository `rushikesh3111/support-ticket-raiser`, pushed branch, deployed backend + frontend with live URLs and verified post-deployment smoke tests.
