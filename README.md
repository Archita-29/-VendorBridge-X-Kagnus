# VendorBridge — Procurement & Vendor Management ERP

A full-stack procurement and vendor management application developed for the Kagnus internship project.

VendorBridge provides an authentication system, role-based API access, vendor management, and a dashboard foundation. The project uses React and TypeScript on the frontend, FastAPI on the backend, and PostgreSQL for persistent storage.

> **Project status:** Week 1 implementation. Core features are implemented, but some flows and production-readiness requirements remain unverified or incomplete. See [Known Limitations](#known-limitations) before using this project.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup and Migrations](#database-setup-and-migrations)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Overview](#api-overview)
- [Roles and Permissions](#roles-and-permissions)
- [Security Notes](#security-notes)
- [Known Limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

## Features

### Authentication and sessions

Implemented:

- User registration API with email validation and password-length validation.
- Login using email and password.
- Password hashing using `pwdlib` and its recommended password-hashing configuration.
- HTTP-only session cookie authentication.
- Server-side session records stored in PostgreSQL.
- Session expiration and logout.
- Authenticated-user endpoint (`/auth/me`).
- Password-reset request and confirmation endpoints.
- Password-reset tokens stored as hashes, with a 30-minute expiration and single-use checks.
- Session revocation after a successful password reset.

**Current limitations:** A registration screen is not yet implemented in the frontend. Password-reset email delivery is not configured. The development-only reset-token response is disabled by default and must never be enabled in production.

### Vendor management

Implemented API operations include:

- Create vendors.
- List and view vendors.
- Update vendor details.
- Delete vendors.
- Search vendor records.
- Filter by vendor status.
- Update vendor status.
- Validate vendor input using Pydantic schemas.
- Handle duplicate GSTIN conflicts and missing records.
- Enforce role checks at the API level.

Vendor fields include:

- Vendor name and category.
- GSTIN and PAN.
- Contact person, email, and phone.
- Address.
- Vendor status.
- Database-generated ID and timestamps.

### Dashboard and frontend

Implemented:

- React and TypeScript application.
- Login screen and authenticated dashboard access.
- Session restoration on page refresh.
- Logout action.
- Vendor listing, search/filter, and vendor creation interface.
- Dashboard summary cards and quick actions.
- Empty states and placeholders for functionality planned for future modules.
- Frontend API client with cookie credentials and error handling.
- Tailwind CSS configuration.

The dashboard is a foundation for future procurement features. Placeholder metrics must not be interpreted as live procurement data.

### Database and migrations

Implemented:

- PostgreSQL database.
- SQLAlchemy ORM models.
- Alembic database migrations.
- User, vendor, session, and password-reset-token tables.
- Persistent PostgreSQL storage through Docker Compose.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | Tailwind CSS, CSS |
| Backend | Python, FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | PostgreSQL |
| Authentication | Password hashing, HTTP-only session cookies |
| Testing | pytest, FastAPI TestClient |
| Local database environment | Docker Compose |
| Version control | Git and GitHub |

## Architecture

```text
Browser
   |
   v
React + TypeScript + Vite
   |
   | HTTP requests with session cookies
   v
FastAPI backend
   |
   +-- Authentication routes
   +-- Vendor management routes
   +-- Dashboard summary route
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
```

The frontend and backend run separately during local development. The frontend uses `http://localhost:8000` for API requests and normally runs at `http://localhost:5173`.

## Prerequisites

Install the following software:

- Git
- Python 3.13 or another compatible Python version
- Node.js 20 or a compatible supported version
- npm
- Docker Desktop with Docker Compose

The commands below assume macOS or Linux and a Bash-compatible terminal.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Archita-29/-VendorBridge-X-Kagnus.git
cd -VendorBridge-X-Kagnus
```

If the repository has already been cloned, open its existing directory instead of cloning it again.

### 2. Configure environment variables

Check whether the root `.env.example` file exists:

```bash
ls -la .env.example
```

If it exists, copy it to `.env`:

```bash
cp .env.example .env
```

If `.env` already exists and contains your local configuration, **do not overwrite it**.

Open `.env` locally and configure the values required by `infra/compose.yaml` and the backend. At minimum, the backend database URL must point to the correct PostgreSQL database, credentials, and port.

For the current local Docker setup, the database is exposed on host port `5433`, while PostgreSQL listens on port `5432` inside the container. The configured database is `vendorbridge`.

A typical SQLAlchemy URL has this structure:

```text
postgresql+psycopg://USERNAME:PASSWORD@localhost:5433/DATABASE_NAME
```

Replace the placeholders with your local values. Do not commit real credentials.

**Important:** Check the actual variable names in `infra/compose.yaml` and `.env.example`. Do not assume that placeholder names above are literal environment variable names.

### 3. Start PostgreSQL

Inspect the Compose configuration:

```bash
cat infra/compose.yaml
```

Start the configured database service:

```bash
docker compose -f infra/compose.yaml up -d
```

Check its status:

```bash
docker compose -f infra/compose.yaml ps
```

The database should become healthy before running migrations or starting the backend.

If your local setup already has the database running, check its status rather than creating another instance or resetting its data.

### 4. Set up the backend

From the repository root:

```bash
cd backend
```

Create a virtual environment if one does not already exist:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install the backend dependencies.

If a `requirements.txt` file exists:

```bash
python -m pip install -r requirements.txt
```

If dependencies are managed through another project file, use that file's documented installation procedure. Verify that the required packages are installed, including FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic Settings, Psycopg, `pwdlib`, and pytest.

### 5. Apply database migrations

From the `backend/` directory, with the virtual environment active:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

The migration revision present at the time of the Week 1 setup was:

```text
8b462a5bf309
```

The database migration history includes the initial users/vendors schema, user sessions, and password-reset tokens.

Do not delete the database, remove its Docker volume, or downgrade migrations as part of normal setup.

### 6. Create an administrator account

A helper script is available at:

```text
backend/scripts/create_admin.py
```

From the `backend/` directory, with the virtual environment active, run:

```bash
python scripts/create_admin.py
```

Follow the prompts. Use a strong, unique password and do not put passwords directly into shell commands.

The script is intended to create an administrator account without promoting an existing account automatically. Review the script before using it in a production environment.

### 7. Set up the frontend

Open another terminal and return to the repository root:

```bash
cd /path/to/-VendorBridge-X-Kagnus/frontend
```

Replace `/path/to/` with the actual location of your cloned repository.

Install dependencies:

```bash
npm ci
```

Build the frontend:

```bash
npm run build
```

Run the development server:

```bash
npm run dev
```

The frontend is normally available at:

http://localhost:5173/

The API is normally available at:

http://localhost:8000/

Interactive API documentation is available at:

http://localhost:8000/docs

**Backend launch note:** Use the backend's configured ASGI entry point. For the current application, it is expected to be `app.main:app`. From the `backend/` directory, run:

```bash
uvicorn app.main:app --reload
```

If the backend is already running on port `8000`, reuse it instead of launching a second instance.

## Environment Configuration

The application reads its backend settings from the root `.env` file.

Relevant settings include:

| Setting | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection URL |
| `APP_NAME` | Application name, if configured |
| `APP_ENV` | Environment name; use development locally |
| `EXPOSE_RESET_TOKEN` | Allows the development-only reset-token response when explicitly enabled |

The exact environment-variable names and defaults should be checked against `backend/app/config.py`, `.env.example`, and the Compose configuration in the checked-out version of the repository.

### Environment safety rules

- Never commit `.env`.
- Never share real database passwords, reset tokens, or other secrets in screenshots or issue reports.
- Keep `.env.example` limited to placeholders and non-secret defaults.
- Rotate any credential that is accidentally exposed.
- Do not enable reset-token exposure outside local development.
- Use a separate database and separate credentials for testing and production.

## Running the Application

A typical local workflow uses three terminals.

**Terminal 1 — Database**

```bash
docker compose -f infra/compose.yaml up -d
```

**Terminal 2 — Backend**

```bash
cd /path/to/-VendorBridge-X-Kagnus/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Terminal 3 — Frontend**

```bash
cd /path/to/-VendorBridge-X-Kagnus/frontend
npm run dev
```

Open `http://localhost:5173/` to use the frontend and `http://localhost:8000/docs` to inspect the API.

### Health check

The backend exposes:

```http
GET /health
```

Expected successful response:

```json
{
  "status": "ok"
}
```

A successful health response confirms that the health endpoint is available; it does not, by itself, prove that every application feature or database operation works.

## Testing

### Backend tests

The repository contains:

- `backend/tests/test_health.py`
- `backend/tests/test_vendor_permissions.py`

Run the tests from the `backend/` directory with the virtual environment active:

```bash
PYTHONPATH=. pytest -q
```

The explicit `PYTHONPATH=.` is currently needed in this local setup so Python can locate the `app` package.

### Tests that have passed

During the recorded Week 1 development session, the following result was observed:

```text
7 passed, 1 warning
```

The tests covered:

- Health endpoint returns HTTP 200 with `{"status": "ok"}`.
- Unauthenticated vendor-list requests are rejected.
- The vendor role-check helper allows the configured directory roles.
- The vendor role is denied access to the directory role-check helper.
- A manager is denied procurement-only permissions by the helper.

The permission tests call the role-check helper directly. They do not replace comprehensive HTTP-level tests for every endpoint.

**Testing status note:** The seven passing tests are a previously observed result. Re-run the tests against the current checkout before treating them as the final result for a new installation or release.

### Frontend build

The following command succeeded during development:

```bash
npm run build
```

It ran the TypeScript build check and Vite production build.

A successful build confirms compilation, not full browser-level or end-to-end correctness.

### Manual test checklist

Use this checklist after setting up the project:

- [ ] Backend starts without configuration errors.
- [ ] `GET /health` returns HTTP 200.
- [ ] Swagger documentation loads.
- [ ] Login succeeds with a valid active account.
- [ ] Invalid login credentials are rejected.
- [ ] Refreshing the browser preserves a valid session.
- [ ] Logout invalidates the session.
- [ ] Unauthenticated vendor API requests are rejected.
- [ ] Authorized users can create and list vendors.
- [ ] Vendor search and status filtering work.
- [ ] Invalid vendor input is rejected.
- [ ] Duplicate GSTIN handling works.
- [ ] Vendor update and deletion work for authorized roles.
- [ ] Manager approval permissions behave as intended.
- [ ] Forgot-password requests return a generic public message.
- [ ] Reset tokens expire and cannot be reused.
- [ ] Successful password reset invalidates existing sessions.
- [ ] Login works with the new password after reset.
- [ ] Frontend build succeeds.
- [ ] `.env` is ignored by Git and contains no committed secrets.

Only mark an item as passed after actually executing and observing the relevant test.

## API Overview

The routes below describe the implemented route structure. See `/docs` for the live schemas, parameters, and response definitions.

### Health and dashboard

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/dashboard/summary` | Dashboard summary |

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate and establish a session |
| GET | `/auth/me` | Return the current authenticated user |
| POST | `/auth/logout` | End the current session |
| POST | `/auth/forgot-password` | Request password-reset instructions |
| POST | `/auth/reset-password` | Reset a password using a valid token |

### Vendors

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/vendors/` | List vendors with supported search/filter options |
| POST | `/vendors/` | Create a vendor |
| GET | `/vendors/{vendor_id}` | View a vendor |
| PUT | `/vendors/{vendor_id}` | Update vendor details |
| PATCH | `/vendors/{vendor_id}/status` | Change vendor status |
| DELETE | `/vendors/{vendor_id}` | Delete a vendor |

Protected endpoints require a valid session and the appropriate role. Exact permissions and validation rules are enforced by the backend, not just by frontend visibility.

## Roles and Permissions

The current backend role policy is:

| Role | Vendor directory access |
|---|---|
| Admin | List, view, create, update, delete, and change status |
| Procurement Officer | List, view, create, update, and delete |
| Manager/Approver | List, view, and change status |
| Vendor | Denied access to the shared vendor directory |

The registration endpoint assigns the `vendor` role by default. Public registration must not allow a caller to choose an elevated role.

### Important vendor-role limitation

The current data model does not yet associate a vendor account with its own vendor record. Consequently, vendor users cannot yet securely view or manage their own vendor profile through a dedicated vendor portal.

If that functionality is required, introduce an explicit account-to-vendor relationship and implement ownership checks on the backend before adding those screens.

## Security Notes

This project is intended for local development and internship evaluation. It is not yet certified or hardened for production.

- **Cookies:** The current local configuration uses a non-secure cookie for HTTP development. Production must use HTTPS and secure cookie settings.
- **CSRF:** Review and implement an appropriate CSRF protection strategy before production deployment, especially for cookie-authenticated state-changing operations.
- **Password reset:** The backend has no configured email provider. Development-only token exposure is not a production delivery mechanism.
- **Reset-token exposure:** Keep `EXPOSE_RESET_TOKEN` disabled in production. The application must never reveal reset tokens to public clients in a deployed environment.
- **Sessions:** Server-side sessions are stored in the database. Review session rotation, expiration, cleanup, and concurrency behavior before production.
- **Role assignment:** Public registration creates vendor-role accounts. Administrator privileges should only be granted through a trusted administrative process.
- **Database:** Use least-privilege credentials, secure secret storage, backups, and a separate production database.
- **Validation:** Server-side validation is required even when the frontend performs input checks.
- **Error handling:** Avoid exposing secrets, internal stack traces, or sensitive account details in API responses or logs.
- **Dependencies:** Keep dependencies patched and review security advisories.
- **Testing:** The current test suite is small. Add HTTP-level authorization tests and isolated database tests before relying on the system for sensitive workflows.

## Known Limitations

1. **Email delivery is not implemented.** Password-reset requests create database tokens, but real reset emails are not sent.
2. **Registration UI is missing.** Registration is available through the backend API; the current frontend login screen does not provide a registration form.
3. **Vendor self-service is incomplete.** Vendor accounts are not linked to individual vendor records.
4. **Dashboard metrics are partly placeholders.** Future procurement modules, such as RFQs and purchase orders, are not fully implemented.
5. **Test coverage is limited.** The existing tests cover the health endpoint and role-check helper behavior, but not all authentication and vendor endpoints.
6. **Reset-flow end-to-end verification is still required.** Expiry, single-use behavior, password replacement, and session revocation must be verified against the running application.
7. **Production security work remains.** HTTPS cookie settings, CSRF protection, secret management, email delivery, logging, and deployment hardening require additional work.
8. **No production deployment is documented.** Local development is the primary supported setup.
9. **Git identity may need configuration.** Git can infer a commit identity from the local machine; configure a verified name and email for future commits if necessary.

## Troubleshooting

### Python cannot import `app`

From `backend/`, activate the virtual environment and run:

```bash
PYTHONPATH=. pytest -q
```

For the application server, run the command from the `backend/` directory so that the `app` package is on the Python import path.

### PostgreSQL connection fails

Check:

```bash
docker compose -f infra/compose.yaml ps
```

Confirm that the container is healthy and that the database URL in `.env` matches the configured credentials, database name, and host port. This setup uses host port `5433` for the Docker database.

Do not delete the database volume as a troubleshooting shortcut.

### Port 8000 is already in use

A backend server may already be running. Reuse it or stop the appropriate existing process before starting another server. Do not terminate unrelated processes.

### Frontend requests fail

Check that the backend is reachable at `http://localhost:8000`, that the frontend uses the matching API base URL, and that CORS allows the frontend origin. Cookie-based requests must include credentials.

### Alembic reports an unexpected revision

Run:

```bash
alembic current
alembic history
```

Review the migration history and current database state before applying any corrective action. Do not delete tables or reset the database to make the revision match.

## Future Improvements

- Implement a registration screen.
- Integrate a real email provider for password-reset messages.
- Build a vendor self-service portal with explicit ownership authorization.
- Add comprehensive API and database integration tests.
- Add password-reset, registration, and authorization regression tests.
- Add CSRF protection and production HTTPS cookie configuration.
- Complete dashboard metrics as procurement modules are implemented.
- Add structured logging and monitoring.
- Document deployment and backup/recovery procedures.
- Add screenshots and a short demo walkthrough.

## License

No license has been specified yet. All rights and permitted uses should be clarified before redistributing the project.