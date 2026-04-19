# LiveNeed — AI-Powered Smart Resource Allocation Platform

## 🚀 Live Prototype Links
- **Frontend App**: [Insert Vercel/Netlify Link Here]
- **Backend API Docs**: [Insert Render/Railway Link Here]/docs
- **Pitch Video / Demo**: [Insert YouTube/Drive Link Here]

LiveNeed is a full-stack platform that connects **community needs** with **volunteers** using NLP-powered analysis. It ingests need reports via text or voice, extracts structured information using spaCy, scores urgency, matches the best-fit volunteers based on skills and proximity, and tracks fulfillment through a Proof-of-Impact system.

---

## Features

- **AI-Powered Need Analysis** — spaCy NER extracts locations, people, and organizations. Keyword classification categorizes needs (medical, food, shelter, safety, education). Urgency scoring (0–100) prioritizes critical requests.
- **Smart Volunteer Matching** — Skill-based scoring (+50 primary match, +10 secondary) combined with Haversine proximity scoring (max +50 within 100km).
- **Voice Input** — Submit needs via voice using the Web Speech API (Chrome/Edge).
- **Real-Time Dashboard** — Prioritized need cards with urgency color-coding, stats overview, auto-refresh every 30 seconds.
- **Proof-of-Impact** — Volunteers verify fulfillment with notes/photos. Needs transition: pending → assigned → fulfilled.
- **77 Automated Tests** — Unit, integration, and end-to-end tests using pytest + Hypothesis.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS 3 |
| Backend | FastAPI (Python), SQLAlchemy, SQLite |
| AI/NLP | spaCy (en_core_web_sm) |
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
│                     │                   │  • /match           │
└─────────────────────┘                   │  • /assign          │
                                          │  • /verify-impact   │
                                          │  • /stats           │
                                          │  • /assignments     │
                                          └────────┬────────────┘
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
│   ├── models.py               # ORM models (User, Need, Assignment, ImpactLog)
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── matching_engine.py      # Skill + proximity scoring engine
│   ├── seed.py                 # Demo data seeder (10 needs + 6 volunteers)
│   ├── routers/
│   │   ├── needs.py            # /submit-need, /analyze, /prioritize, /stats
│   │   ├── matching.py         # /match
│   │   ├── assignments.py      # /assign, /assignments
│   │   ├── impact.py           # /verify-impact
│   │   └── volunteers.py       # /register-volunteer
│   ├── ai/
│   │   ├── nlp_processor.py    # spaCy entity extraction + classification
│   │   └── urgency_scorer.py   # Urgency scoring (0–100)
│   └── tests/                  # 8 test files, 77 tests
│       ├── conftest.py
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
│       │   └── VolunteerReg.jsx
│       └── components/
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

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Seed demo data
python seed.py

# Start server
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npx vite --port 5173
```

Open http://localhost:5173 in your browser.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL (set in frontend) |

---

## API Endpoints

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

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

**77 tests** covering:
- NLP processor (entity extraction, all 6 categories, edge cases)
- Urgency scorer (range bounds, emergency thresholds, recency bonus, capping)
- Matching engine (skill scoring, proximity scoring, sorting, edge cases)
- All API endpoints (success paths, 404/409/403/422 error paths)
- Full end-to-end workflow (submit → analyze → match → assign → verify)

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
