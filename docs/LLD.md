# Low-Level Design (LLD) — Support Ticket Raiser System

## 1. Database Schema & ERD

### Tables
- **`users`**:
  - `id`: Integer (PK, AutoIncrement)
  - `name`: String(100)
  - `email`: String(150), Unique, Indexed
  - `hashed_password`: String(255)
  - `role`: Enum (`admin`, `agent`, `user`)
  - `department`: String(100)
  - `is_active`: Boolean (default True)
  - `created_at`: DateTime

- **`tickets`**:
  - `id`: Integer (PK, AutoIncrement)
  - `title`: String(255), Indexed
  - `description`: Text
  - `status`: Enum (`Open`, `In Progress`, `On Hold`, `Resolved`, `Closed`, `Archived`)
  - `priority`: Enum (`Low`, `Medium`, `High`, `Critical`)
  - `category`: Enum (`IT Support`, `Hardware`, `Software`, `Network`, `Billing`, `Access Request`, `Other`)
  - `created_by`: Integer (FK `users.id`)
  - `assigned_to`: Integer (FK `users.id`, Nullable)
  - `created_at`: DateTime
  - `updated_at`: DateTime
  - `resolved_at`: DateTime (Nullable)
  - `closed_at`: DateTime (Nullable)
  - `response_due_at`: DateTime (Nullable)
  - `resolution_due_at`: DateTime (Nullable)
  - `first_responded_at`: DateTime (Nullable)
  - `is_response_breached`: Boolean (default False)
  - `is_resolution_breached`: Boolean (default False)

- **`comments`**:
  - `id`: Integer (PK)
  - `ticket_id`: Integer (FK `tickets.id` ON DELETE CASCADE)
  - `author_id`: Integer (FK `users.id`)
  - `message`: Text
  - `is_internal`: Boolean (default False)
  - `created_at`: DateTime

- **`attachments`**:
  - `id`: Integer (PK)
  - `ticket_id`: Integer (FK `tickets.id` ON DELETE CASCADE)
  - `uploaded_by`: Integer (FK `users.id`)
  - `filename`: String(255)
  - `file_path`: String(500)
  - `file_size`: Integer
  - `content_type`: String(100)
  - `uploaded_at`: DateTime

- **`audit_logs`**:
  - `id`: Integer (PK)
  - `ticket_id`: Integer (FK `tickets.id` ON DELETE CASCADE)
  - `performed_by`: Integer (FK `users.id`, Nullable)
  - `action`: String(100)
  - `details`: Text (Nullable)
  - `meta_info`: JSON (Nullable)
  - `timestamp`: DateTime

- **`sla_policies`**:
  - `id`: Integer (PK)
  - `priority`: Enum (Unique)
  - `response_time_mins`: Integer
  - `resolution_time_mins`: Integer
  - `description`: String(255)

- **`notifications`**:
  - `id`: Integer (PK)
  - `user_id`: Integer (FK `users.id`)
  - `ticket_id`: Integer (FK `tickets.id`, Nullable)
  - `title`: String(200)
  - `message`: Text
  - `channel`: String(50)
  - `is_read`: Boolean (default False)
  - `created_at`: DateTime

- **`kb_articles`**:
  - `id`: Integer (PK)
  - `title`: String(255)
  - `content`: Text
  - `category`: String(100)
  - `tags`: String(255) (Nullable)
  - `created_at`: DateTime

## 2. API Contract Specification

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register new user account | No |
| POST | `/api/v1/auth/login` | Form data login (OAuth2) | No |
| POST | `/api/v1/auth/login/json` | JSON payload login | No |
| GET  | `/api/v1/auth/me` | Fetch active user profile | Bearer JWT |
| GET  | `/api/v1/tickets/` | Paginated ticket listing & search | Bearer JWT |
| POST | `/api/v1/tickets/` | Create support ticket | Bearer JWT |
| GET  | `/api/v1/tickets/{id}` | Ticket details, comments, audit logs | Bearer JWT |
| PUT  | `/api/v1/tickets/{id}` | State transition & assignment | Agent / Admin |
| DELETE| `/api/v1/tickets/{id}` | Archive / soft-delete ticket | Admin only |
| POST | `/api/v1/tickets/{id}/comments/` | Add comment or internal note | Bearer JWT |
| GET  | `/api/v1/tickets/{id}/comments/` | List comments (filtered for users) | Bearer JWT |
| POST | `/api/v1/tickets/{id}/attachments` | Upload attachment file | Bearer JWT |
| GET  | `/api/v1/tickets/{id}/attachments` | List ticket attachments | Bearer JWT |
| GET  | `/api/v1/attachments/{id}/download` | Download attachment file | Bearer JWT |
| GET  | `/api/v1/sla/policies` | List SLA policies | Bearer JWT |
| POST | `/api/v1/sla/policies` | Create or update SLA policy | Admin only |
| POST | `/api/v1/sla/trigger-check` | Check & compute SLA breaches | Staff |
| GET  | `/api/v1/reports/sla-compliance` | SLA metrics breakdown | Staff |
| GET  | `/api/v1/reports/agent-performance`| Agent resolution stats | Staff |
| GET  | `/api/v1/reports/ticket-volume` | Volume distribution stats | Staff |
| GET  | `/api/v1/tickets/{id}/history` | Audit trail history | Bearer JWT |
| GET  | `/api/v1/notifications/` | User notifications | Bearer JWT |
| PUT  | `/api/v1/notifications/{id}/read` | Mark notification read | Bearer JWT |
| PUT  | `/api/v1/notifications/read-all` | Mark all read | Bearer JWT |
| GET  | `/api/v1/kb/` | Search and list Knowledge Base articles | No |
| POST | `/api/v1/kb/` | Publish new KB article | Staff |
| GET  | `/api/v1/kb/{article_id}` | Get full article content | No |
| POST | `/api/v1/actions/tickets/bulk` | Bulk status / assignment operations | Staff |
| POST | `/api/v1/actions/tickets/{id}/csat` | Submit 5-star CSAT survey feedback | Customer / Owner |
| WS   | `/ws/tickets/{ticket_id}` | Live ticket websocket updates | Token param |

## 3. State Machine Logic
- Transition Matrix:
  - `Open` -> `In Progress`, `On Hold`, `Resolved`, `Closed`
  - `In Progress` -> `On Hold`, `Resolved`, `Closed`
  - `On Hold` -> `In Progress`, `Resolved`, `Closed`
  - `Resolved` -> `Closed`, `In Progress` (Re-open)
  - `Closed` -> Terminal (no direct edits)
  - `Archived` -> Administrative soft-delete
