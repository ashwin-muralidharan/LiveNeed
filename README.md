# LiveNeed — AI-Powered Smart Resource Allocation Platform

LiveNeed is a full-stack platform that connects **community needs** with **volunteers** using NLP-powered analysis. It ingests need reports via text or voice, extracts structured information using spaCy, scores urgency, matches the best-fit volunteers based on skills and proximity, and tracks fulfillment through a Proof-of-Impact system.

---

## Features

- **AI-Powered Need Analysis** — spaCy NER extracts locations, people, and organizations. Keyword classification categorizes needs (medical, food, shelter, safety, education). Urgency scoring (0–100) prioritizes critical requests.
- **Smart Volunteer Matching** — Skill-based scoring (+50 primary match, +10 secondary) combined with Haversine proximity scoring (max +50 within 100km).
- **Voice Input** — Submit needs via voice using the Web Speech API (Chrome/Edge).
- **Real-Time Dashboard** — Prioritized need cards with urgency color-coding, stats overview, auto-refresh every 30 seconds.
- **Admin Panel** — Secured with JWT authentication. Manage needs (change status, delete), volunteers (edit, activate/deactivate, remove), and approve new admin registrations.
- **Proof-of-Impact** — Volunteers verify fulfillment with notes/photos. Needs transition: pending → assigned → fulfilled.
- **104 Automated Tests** — Unit, integration, and end-to-end tests using pytest + Hypothesis.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS 3 |
| Backend | FastAPI (Python), SQLAlchemy, SQLite |
| AI/NLP | spaCy (en_core_web_sm) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Testing | pytest, Hypothesis, FastAPI TestClient |
| Voice | Web Speech API (browser-native) |

---

## Architecture

```
┌─────────────────────┐     REST API      ┌─────────────────────┐
│   React Frontend    │ ◄──────────────► │   FastAPI Backend   │
│                     │                   │                     │
│  • Dashboard        │                   │  • /submit-need     │
│  • Submit Need      │                   │  • /analyze         │
│  • Volunteer Reg    │                   │  • /prioritize      │
│  • Admin Panel 🔒   │                   │  • /match           │
│  • Admin Login      │                   │  • /admin/* 🔒      │
│                     │                   │  • /auth/*          │
└─────────────────────┘                   └────────┬────────────┘
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                               ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
                               │  spaCy  │   │Matching │   │ SQLite  │
                               │   NLP   │   │ Engine  │   │   DB    │
                               └─────────┘   └─────────┘   └─────────┘
```

---

## Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM models (User, Need, Assignment, ImpactLog, AdminUser)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── matching_engine.py      # Skill + proximity scoring engine
│   ├── seed.py                 # Demo data seeder (10 needs + 6 volunteers)
│   ├── requirements.txt        # Python dependencies
│   ├── routers/
│   │   ├── needs.py            # /submit-need, /analyze, /prioritize, /stats
│   │   ├── matching.py         # /match
│   │   ├── assignments.py      # /assign, /assignments
│   │   ├── impact.py           # /verify-impact
│   │   ├── volunteers.py       # /register-volunteer
│   │   ├── admin.py            # /admin/* (JWT-protected management endpoints)
│   │   └── auth.py             # /auth/* (login, register, approve/reject)
│   ├── ai/
│   │   ├── nlp_processor.py    # spaCy entity extraction + classification
│   │   └── urgency_scorer.py   # Urgency scoring (0–100)
│   └── tests/                  # 9 test files, 104 tests
│       ├── conftest.py
│       ├── test_api_admin.py
│       ├── test_api_assignments.py
│       ├── test_api_impact.py
│       ├── test_api_matching.py
│       ├── test_api_needs.py
│       ├── test_api_volunteers.py
│       ├── test_matching_engine.py
│       ├── test_nlp_processor.py
│       └── test_urgency_scorer.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── index.css
│       ├── main.jsx
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── SubmitNeed.jsx
│       │   ├── VolunteerReg.jsx
│       │   ├── Admin.jsx
│       │   ├── AdminLogin.jsx
│       │   └── AdminRegister.jsx
│       └── components/
│           ├── AuthContext.jsx
│           ├── NeedCard.jsx
│           ├── StatsBar.jsx
│           ├── UrgencyBadge.jsx
│           ├── VoiceInput.jsx
│           ├── MatchModal.jsx
│           └── Toast.jsx
```

---

## Setup & Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+

### Step 1 — Backend

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Seed demo data (10 needs + 6 volunteers)
python seed.py

# Start backend server
uvicorn main:app --reload --port 8000
```

The backend will start at **http://localhost:8000**
API docs available at: **http://localhost:8000/docs**

> **Note:** On first startup, two default admin accounts are auto-created:
> - `maneesh@gmail.com` / `12345`
> - `ashwin@gmail.com` / `12345`

### Step 2 — Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start frontend dev server
npx vite --port 5173
```

The frontend will start at **http://localhost:5173**

### Step 3 — Open in Browser

1. Go to **http://localhost:5173** — you'll see the Dashboard
2. Navigate using the top nav: Dashboard, Report Need, Volunteer, Admin
3. The **Admin** page requires login — use the credentials above

---

## Admin Panel Access

The Admin Panel is protected with JWT authentication.

| Action | URL |
|---|---|
| Admin Login | http://localhost:5173/admin/login |
| Admin Register (new admin) | http://localhost:5173/admin/register |
| Admin Panel (after login) | http://localhost:5173/admin |

### Default Admin Accounts

| Email | Password |
|---|---|
| `maneesh@gmail.com` | `12345` |
| `ashwin@gmail.com` | `12345` |

### New Admin Registration Flow
1. New admin visits `/admin/register` and fills in name, email, password
2. Account is created in **pending** status
3. An existing admin logs in and goes to the **Approvals** tab
4. Existing admin clicks **Approve** or **Reject**
5. Once approved, the new admin can log in

---

## API Endpoints

### Public Endpoints (no auth required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/submit-need` | Submit a community need (text + optional location) |
| POST | `/analyze` | Run NLP analysis on a need (entities, category, urgency) |
| GET | `/prioritize` | List active needs sorted by urgency (DESC) |
| GET | `/stats` | Dashboard stats (active, fulfilled, volunteers) |
| POST | `/match` | Find and rank matching volunteers for a need |
| POST | `/assign` | Assign a volunteer to a need |
| GET | `/assignments` | List all active assignments |
| POST | `/verify-impact` | Submit proof of fulfillment |
| POST | `/register-volunteer` | Register a new volunteer with skills/location |

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Login with email + password → JWT token |
| POST | `/auth/register` | Register new admin (pending approval) |
| GET | `/auth/me` | Verify current token (🔒 auth required) |
| GET | `/auth/pending` | List pending admin registrations (🔒) |
| POST | `/auth/approve/{id}` | Approve a pending admin (🔒) |
| POST | `/auth/reject/{id}` | Reject a pending admin (🔒) |

### Admin Endpoints (🔒 JWT auth required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/volunteers` | List all volunteers |
| PATCH | `/admin/volunteers/{id}` | Update volunteer (name, skills, active status) |
| DELETE | `/admin/volunteers/{id}` | Remove a volunteer |
| GET | `/admin/needs` | List all needs (including fulfilled) |
| PATCH | `/admin/needs/{id}/status` | Change need status (pending/assigned/fulfilled) |
| DELETE | `/admin/needs/{id}` | Remove a need |

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

**104 tests** covering:
- NLP processor (entity extraction, all 6 categories, edge cases)
- Urgency scorer (range bounds, emergency thresholds, recency bonus, capping)
- Matching engine (skill scoring, proximity scoring, sorting, edge cases)
- All API endpoints (success paths, 404/409/403/422 error paths)
- Admin authentication (login, register, approve, reject, JWT validation)
- Full end-to-end workflow (submit → analyze → match → assign → verify)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL (set in frontend) |

---

## Deployment

### Backend
- **Platform**: Google Cloud Run, Render, or any Docker-compatible host
- **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Build command**: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- **Note**: SQLite is file-based; for production, consider PostgreSQL

### Frontend
- **Platform**: Firebase Hosting, Vercel, or Netlify
- **Build command**: `npm run build` (outputs to `dist/`)
- **Environment**: Set `VITE_API_URL` to the deployed backend URL

---

## License

Built for Google Hackathon 2026.
