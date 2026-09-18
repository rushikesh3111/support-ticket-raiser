# 🎯 IMPROVED PI IMPLEMENTATION PROMPT (USE CONFIGURED MODEL)
## Support Ticket Raiser — Full Autonomous SDLC Implementation

---

## 🎯 OBJECTIVE
Implement the **Support Ticket Raiser** system (per `final_support_tic.md`) using **Pi with its configured model** via the **full autonomous SDLC loop** defined in `AGENTS.md` / `SDLC-AGENT.md`.

**Deliverable:** A production-ready, deployed Support Ticket Raiser with:
- ✅ Full FastAPI backend + React frontend
- ✅ **10+ test cases per endpoint** (zero missing)
- ✅ Complete HLD/LLD/TESTING docs
- ✅ GitHub repo with CI/CD
- ✅ **Live deployment URL** for frontend
- ✅ Backend API accessible

---

## 📋 EXECUTION CONTEXT

### Workspace
```
Project dir: /home/rushi/SDLC-WORKFLOW
Git repo:    (create new: rushikesh3111/support-ticket-raiser)
Branch:      feature/support-ticket-raiser-mvp
```

### Model & Tools
| Component | Configuration |
|---|---|
| **Model** | Use pi-agent's **configured default model** (whatever is set in pi-agent config) |
| **Pi Wrapper** | `~/.local/bin/pi-agent` |
| **GitHub Account** | `rushikesh3111` |

---

## 🔄 FULL AUTONOMOUS SDLC LOOP (MANDATORY SEQUENCE)

Execute **every step in order** — do not skip, do not stop until complete:

### Phase 1: BACKLOG & PLANNING
- [ ] Create `BACKLOG.md` with all tasks from `final_support_tic.md` (use FR-1 through FR-10, NFR table)
- [ ] Prioritize: MVP first (Auth, Tickets CRUD, Comments, Attachments, Basic RBAC, Email Notifications)
- [ ] Create feature branch: `git checkout -b feature/support-ticket-raiser-mvp`

### Phase 2: IMPLEMENTATION (via Pi)
For **each module** in sequence:
1. **Auth Module** — JWT, OAuth2, RBAC (User/Agent/Admin)
2. **Ticket Module** — CRUD, status transitions, assignment
3. **Comment Module** — threaded conversations
4. **Attachment Module** — file upload (local/S3)
4. **SLA Module** — Celery/APScheduler background jobs
5. **Notification Module** — Email (SES/SendGrid) + Webhook
6. **Reporting Module** — SLA compliance, agent performance
7. **Audit Module** — middleware logging
8. **Frontend** — React + TypeScript + Tailwind (dashboard, ticket list, detail, admin)

**For EACH module, Pi must:**
- Write code following `final_support_tic.md` structure (Section 3.4)
- Follow FastAPI project structure exactly (Section 3.4)
- Use SQLAlchemy 2.0 async + Alembic migrations
- Use Pydantic v2 schemas for all requests/responses
- Implement RBAC via FastAPI `Depends()`
- Write unit + integration tests **in the same pass**

### Phase 3: TESTING — 10+ TEST CASES PER ENDPOINT (ZERO MISSING)

**MANDATORY:** Every endpoint from Section 3.5 must have **≥10 test cases** covering:

| Endpoint | Minimum Test Cases (must all pass) |
|---|---|
| `POST /api/v1/auth/login` | Valid creds → token; invalid password → 401; inactive user → 403; malformed → 422; rate limit → 429; token expiry; refresh token; logout |
| `POST /api/v1/tickets/` | Valid ticket → 201; missing fields → 422; unauth → 401; oversized attachment → 413; invalid category; duplicate; large description; concurrent create; RBAC |
| `GET /api/v1/tickets/` | Pagination; filters (status/priority/category/assignee/date); empty results; RBAC filtering; sort; search |
| `GET /api/v1/tickets/{id}` | 200 detail; 404 not found; 403 unauthorized; audit trail included |
| `PUT /api/v1/tickets/{id}` | Valid transition; invalid transition (400); unauthorized (403); concurrent conflict; audit log entry |
| `DELETE /api/v1/tickets/{id}` | Soft delete (200); already deleted (409); non-admin (403); cascade |
| `POST /tickets/{id}/comments` | Valid comment (201); empty (422); on closed ticket (business rule); long text; mentions |
| `GET /tickets/{id}/history` | Chronological; empty for new; 403 unauthorized; pagination |
| `POST /tickets/{id}/attachments` | Valid file (201); invalid type (400); oversized (413); virus scan hook; multiple |
| `GET /reports/sla-compliance` | Correct % calculation; empty data; date range; agent filter |
| `GET /api/v1/reports/agent-performance` | Correct aggregation; date range; agent filter; zero data |
| `WS /ws/tickets/{id}` | Real-time updates; reconnect; unauthorized rejection; concurrent clients |

**PLUS cross-cutting tests (each ≥5 cases):**
- **Security:** RBAC bypass attempts, SQL injection, XSS, path traversal, rate limiting
- **Performance:** p95 < 500ms, concurrent load (20 users), memory leak check
- **Regression:** Full suite re-run after each module

**ALL tests must pass** — re-run independently by main agent. **No test skipped, no test faked.**

### Phase 4: DOCUMENTATION (AUTO-UPDATE)
Create/update in `/docs`:
- **HLD.md** — Architecture, tech stack, data flow, security, deployment diagram
- **LLD.md** — DB schema (ERD), API contracts, class diagrams, state machines
- **TESTING.md** — Full test matrix, results per endpoint, coverage report

### Phase 5: GIT, GITHUB & CI/CD
- [ ] `git add .`, `git commit -m "feat: <module>"` per module
- [ ] `git push origin feature/support-ticket-raiser-mvp`
- [ ] `gh repo create rushikesh3111/support-ticket-raiser --public --source=. --push`
- [ ] Create `.github/workflows/ci.yml`:
  - Lint (ruff/flake8)
  - Unit + integration tests (pytest)
  - Security scan (bandit)
  - Build Docker images
  - Deploy to staging on PR merge
- [ ] `gh pr create --title "feat: Support Ticket Raise MVP" --body "..."`
- [ ] `gh pr merge --squash --delete-branch`

### Phase 6: DEPLOYMENT (LIVE URL REQUIRED)
**Backend:**
- Dockerize: `Dockerfile` + `docker-compose.yml` (FastAPI + PostgreSQL + Redis + Celery)
- Deploy to: **Fly.io** / **Railway** / **Render** / **Single VM** (choose one, document)
- PostgreSQL: managed (Neon/Supabase/Cloud SQL) or self-hosted
- Redis: managed or self-hosted

**Frontend:**
- `npm run build` → static assets
- Deploy to: **Vercel** / **Netlify** / **Cloudflare Pages** / **Same VM via Nginx**
- **Must provide: LIVE FRONTEND URL** (e.g., `https://support-ticket-raiser.vercel.app`)

**API Base URL:** `https://api.support-ticket-raiser.fly.dev/v1` (or equivalent)

### Phase 6: SMOKE TEST DEPLOYMENT
- [ ] `curl https://<api-url>/health` → 200
- [ ] `curl https://<api-url>/api/v1/auth/login` → works
- [ ] Frontend loads at live URL, can create ticket end-to-end
- [ ] SLA background job runs (check logs)

### Phase 7: BACKLOG UPDATE
- [ ] Update `BACKLOG.md` → `[x] Completed` for all MVP tasks
- [ ] Add follow-up tasks for post-MVP (SLA automation, integrations, KB, etc.)

---

## 🚫 NON-NEGOTIABLE RULES (from AGENTS.md / SDLC-AGENT.md)

| Rule | Enforcement |
|---|---|
| **Use configured model** | Use pi-agent's configured default model |
| **10+ tests per endpoint** | Zero tolerance for missing tests |
| **Independent verification** | Main agent re-runs ALL tests independently |
| **Docs auto-update** | HLD/LLD/TESTING.md updated every module |
| **No hardcoded secrets** | `.env.example` only, real secrets via platform |
| **Branch per task** | `feature/<task-name>`, squash merge |
| **GitHub CI/CD** | `.github/workflows/ci.yml` mandatory |
| **Live URL required** | Frontend URL must be provided at end |

---

## 📦 EXECUTION COMMAND

Run this **single command** to start the full autonomous loop:

```bash
cd /home/rushi/SDLC-WORKFLOW && pi-agent \
  -- "
  IMPLEMENT THE SUPPORT TICKET RAISER SYSTEM PER final_support_tic.md
  
  WORKSPACE: /home/rushi/SDLC-WORKFLOW
  GIT REPO: rushikesh3111/support-ticket-raiser
  BRANCH: feature/support-ticket-raiser-mvp
  
  EXECUTE THE FULL AUTONOMOUS SDLC LOOP:
  1. Create BACKLOG.md from final_support_tic.md requirements
  2. Create feature branch
  3. Implement ALL modules (Auth, Tickets, Comments, Attachments, SLA, Notifications, Reports, Audit, Frontend)
  4. Write ≥10 tests PER ENDPOINT (zero missing), run pytest, verify all pass
  5. Generate HLD.md, LLD.md, TESTING.md in /docs
  5. Git commit/push per module, create GitHub repo, CI/CD workflow
  6. Deploy backend + frontend, provide LIVE FRONTEND URL
  5. Smoke test deployment, update BACKLOG.md
  
  USE PI-AGENT'S CONFIGURED DEFAULT MODEL.
  FOLLOW AGENTS.md / SDLC-AGENT.md RULES STRICTLY.
  REPORT PROGRESS AT EACH PHASE.
  FINAL DELIVERABLE: LIVE FRONTEND URL + API URL + GITHUB REPO URL
  "
```

---

## ✅ SUCCESS CRITERIA (ALL MUST BE MET)

| Criterion | Target |
|---|---|
| **GitHub Repo** | `https://github.com/rushikesh3111/support-ticket-raiser` |
| **Live Frontend URL** | `https://<your-deployment>.vercel.app` (or equivalent) |
| **API Base URL** | `https://<api-host>/api/v1` |
| **Test Coverage** | ≥10 tests/endpoint, all passing, >80% coverage |
| **Documentation** | HLD.md, LLD.md, TESTING.md complete |
| **CI/CD** | GitHub Actions passing |
| **BACKLOG.md** | All MVP tasks `[x] Completed` |

---

## 🚀 EXECUTE NOW

Copy the **Execution Command** above and run it. The autonomous loop will execute all phases and report back with:
1. **GitHub repo URL**
2. **Live Frontend URL** 
3. **API Base URL**
4. **Test summary (120+ tests)**
4. **Documentation links**