# LiveNeed Architecture
========================

The LiveNeed platform is structured as a decoupled full-stack application, ensuring scalability, maintainability, and clear separation of concerns.

## ASCII Architecture Diagram

```text
       [ Users / Volunteers ]
                |
                v
  +-----------------------------+
  |                             |
  |     React 18 Frontend       |  (Hosted on Vercel/Netlify)
  |     (Vite + TailwindCSS)    |
  |                             |
  +-----------------------------+
                |
                | JSON via REST API
                |
                v
  +-----------------------------+
  |                             |
  |    FastAPI Web Server       |  (Hosted on Render/Railway)
  |    (Python 3.11+)           |
  |                             |
  +-------------+---------------+
                |
    +-----------+-----------+
    |                       |
    |  AI & Logic Modules   |
    |                       |
    +---+---+---+---+---+---+
        |   |   |   |   |
  +-----+   |   |   |   +-----+
  | NLP     |   |   | Matching |
  | Engine  |   |   | Engine   |
  | (spaCy) |   |   | (Proxim) |
  +---------+   |   +----------+
                |
                v
  +-----------------------------+
  |                             |
  |     Database Layer          |  (SQLite for Prototype -> Postgres for Prod)
  |     (SQLAlchemy ORM)        |
  |                             |
  +-----------------------------+
```

## System Components

1. **Frontend**: React application bundled with Vite. Handles all UI rendering, routing, voice-to-text API interactions, and state management.
2. **Backend**: FastAPI instance providing highly performant, asynchronous API endpoints.
3. **AI Pipeline**: 
    - `NLP Engine`: Uses `spaCy` to extract Named Entities (Locations, Persons) from incoming community needs.
    - `Urgency Scorer`: Algorithm allocating a 0-100 severity index based on keyword mapping and timing.
4. **Matching Engine**: Coordinates Volunteer skills and geographic coordinates (Haversine formula) to generate an actionable queue of matches.
5. **Database**: Relational structure mapping Users to Requests and Actions (Impact Logs). Currently SQLite, but fully abstracted via SQLAlchemy for easy migration to Postgres.
