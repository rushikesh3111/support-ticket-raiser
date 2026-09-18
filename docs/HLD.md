# High-Level Design (HLD) — Support Ticket Raiser System

## 1. System Overview
The Support Ticket Raiser System is an enterprise-grade, modular monolithic support desk application built with FastAPI (Python 3.12) and React.js. It caters to small support operations (10–20 concurrent support staff and end users) requiring full ticket lifecycle management, role-based access control (RBAC), Service Level Agreement (SLA) tracking, real-time updates, audit logging, and reporting.

## 2. Monolithic Architecture & Components
```
                      +-----------------------------+
                      |   React 18 + Tailwind CSS   |
                      |   (Vite SPA Client)         |
                      +--------------+--------------+
                                     | HTTP / WebSocket
                                     v
                      +-----------------------------+
                      |     Uvicorn / ASGI Server   |
                      +--------------+--------------+
                                     |
    +--------------------------------+--------------------------------+
    |                    FastAPI Modular Monolith                     |
    |                                                                 |
    |  +---------------+  +---------------+  +---------------------+  |
    |  |  Auth Router  |  | Ticket Router |  |   Comments Router   |  |
    |  |  (JWT / RBAC) |  | (Lifecycle)   |  |  (Public/Internal)  |  |
    |  +---------------+  +---------------+  +---------------------+  |
    |  +---------------+  +---------------+  +---------------------+  |
    |  | Attachments   |  |  SLA Engine   |  |   Notifications     |  |
    |  | (Local Disk)  |  |  (Policies)   |  |   (In-App & Alerts) |  |
    |  +---------------+  +---------------+  +---------------------+  |
    |  +---------------+  +---------------+  +---------------------+  |
    |  | Audit Router  |  | Reports Router|  |  WebSocket Manager  |  |
    |  | (Compliance)  |  | (Metrics/SLA) |  |  (Live Updates)     |  |
    |  +---------------+  +---------------+  +---------------------+  |
    +--------------------------------+--------------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |   SQLAlchemy 2.0 ORM        |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   SQLite / PostgreSQL DB    |
                      +-----------------------------+
```

## 3. Core Subsystems
1. **Authentication & Authorization Subsystem**:
   - OAuth2 Password Bearer with JWT (HS256).
   - Role-Based Access Control (RBAC): `admin`, `agent`, `user`.
2. **Ticket Lifecycle Subsystem**:
   - Status flow: `Open` -> `In Progress` -> `On Hold` -> `Resolved` -> `Closed` (with `Archived` soft-delete for admins).
   - Dynamic SLA calculation upon ticket creation and priority shifts.
3. **Conversations & Collaboration Subsystem**:
   - Threaded comments per ticket.
   - Support for private staff notes (`is_internal=True`), completely hidden from customers.
4. **File Attachments Subsystem**:
   - Safe disk-backed file storage with extension validation and size safeguards (max 10MB).
5. **SLA Monitoring Subsystem**:
   - Automated deadline enforcement for first response and final resolution.
   - Evaluates ticket age, priority policy thresholds, and triggers breach notifications.
6. **Audit & Compliance Subsystem**:
   - Immutable audit trail recording every state change, assignment, file upload, or comment.
7. **Reporting & Analytics Subsystem**:
   - Aggregated metrics on SLA compliance rates, agent resolution performance, and ticket volume breakdown.

## 4. Security & Quality Policies
- Password hashing with bcrypt.
- Strict Pydantic v2 validation across all endpoints.
- Ownership guards on tickets and conversation threads preventing unauthorized tenant/user access.
