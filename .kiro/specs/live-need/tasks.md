# Implementation Plan: LiveNeed – AI-Powered Smart Resource Allocation Platform

## Overview

Tasks are ordered for a 24–48 hour hackathon build. Each task builds on the previous, ending with a fully wired, demo-ready application. Start with the backend core, add AI modules, wire the API, then build the frontend on top.

## Tasks

- [x] 1. Project scaffolding and environment setup
  - Create the folder structure as defined in design.md: `backend/`, `backend/routers/`, `backend/ai/`, `backend/tests/`, `frontend/src/pages/`, `frontend/src/components/`
  - Create `backend/requirements.txt` with the exact contents from design.md
  - Create `frontend/package.json` with React 18, Vite, Tailwind CSS, Axios, and React Router dependencies
  - Create `backend/main.py` as a minimal FastAPI app that mounts the three routers and enables CORS
  - Create `frontend/src/api.js` as an Axios client that reads `VITE_API_URL` from env
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2. Database models and persistence layer
  - [x] 2.1 Implement SQLAlchemy ORM models in `backend/models.py`
    - Define `User`, `Need`, `Assignment`, and `ImpactLog` tables exactly as specified in the Data Models section of design.md
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  - [x] 2.2 Implement `backend/database.py`
    - Create SQLAlchemy engine pointing to `live_need.db` SQLite file
    - Implement `get_db` dependency and `init_db()` function that calls `Base.metadata.create_all`
    - Call `init_db()` on FastAPI startup event in `main.py`
    - _Requirements: 9.5_
  - [x] 2.3 Implement Pydantic schemas in `backend/schemas.py`
    - Define all request and response schemas from design.md: `SubmitNeedRequest`, `AnalyzeRequest`, `MatchRequest`, `VerifyImpactRequest`, `NeedResponse`, `VolunteerMatchResult`
    - _Requirements: 8.1, 8.2, 8.4, 8.5_
  - [ ]* 2.4 Write property test for data persistence round trip
    - **Property 1: Non-empty submission always creates a need**
    - **Validates: Requirements 1.1, 1.3**
    - In `tests/conftest.py`, create a pytest fixture that spins up an in-memory SQLite test database and a FastAPI `TestClient`
    - Use Hypothesis `@given(st.text(min_size=1).filter(lambda s: s.strip()))` to generate random non-empty descriptions, POST to `/submit-need`, and assert a need ID is returned and the DB record exists with matching text
    - `# Feature: live-need, Property 1: Non-empty submission always creates a need`

- [x] 3. NLP processing module
  - [x] 3.1 Implement `backend/ai/nlp_processor.py`
    - Load `en_core_web_sm` spaCy model once at module level
    - Implement `process_need_text(text: str) -> NLPResult` that extracts GPE/PERSON/ORG entities using spaCy and classifies category using the `CATEGORY_KEYWORDS` dict from design.md
    - Return a dataclass/TypedDict with `entities`, `category`, and `urgency_signals` fields
    - Default to category="other" and empty lists when no matches are found
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ]* 3.2 Write property test: NLP output is always a valid structured object
    - **Property 5: NLP output is always a valid structured object**
    - **Validates: Requirements 2.3, 2.4**
    - Use Hypothesis `@given(st.text(min_size=1))` to call `process_need_text` with random strings and assert the result always has a `category` field and `urgency_signals` list, never raises
    - `# Feature: live-need, Property 5: NLP output is always a valid structured object`
  - [ ]* 3.3 Write property test: category is always one of the defined values
    - **Property 6: Category is always one of the defined values**
    - **Validates: Requirements 2.2**
    - Use Hypothesis `@given(st.text(min_size=1))` and assert `result.category in {"food", "medical", "shelter", "safety", "education", "other"}`
    - `# Feature: live-need, Property 6: Category is always one of the defined values`

- [x] 4. Urgency scoring module
  - [x] 4.1 Implement `backend/ai/urgency_scorer.py`
    - Implement `compute_urgency(nlp_result: NLPResult, submitted_at: datetime) -> float`
    - Apply the scoring formula from design.md: base category score + emergency keyword bonus (capped at 100) + recency bonus
    - Emergency keywords: "emergency", "critical", "urgent", "dying", "fire", "attack"
    - _Requirements: 3.1, 3.2, 3.4_
  - [ ]* 4.2 Write property test: urgency score is always in range [0, 100]
    - **Property 3: Urgency score is always in range**
    - **Validates: Requirements 3.1**
    - Use Hypothesis `@given(st.text(min_size=1), st.datetimes())` to call `compute_urgency` and assert `0 <= score <= 100`
    - `# Feature: live-need, Property 3: Urgency score is always in range`
  - [ ]* 4.3 Write property test: emergency keywords produce high urgency
    - **Property 4: Emergency keywords produce high urgency**
    - **Validates: Requirements 3.4**
    - Use Hypothesis `@given(st.sampled_from(["emergency","critical","urgent","dying","fire","attack"]), st.text())` to build texts containing an emergency keyword and assert score >= 70
    - `# Feature: live-need, Property 4: Emergency keywords produce high urgency`

- [x] 5. Checkpoint – core AI modules working
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Needs API router
  - [x] 6.1 Implement `backend/routers/needs.py` with three endpoints
    - `POST /submit-need`: validate non-empty text (raise 422 if whitespace-only), insert Need with status="pending", return `{ need_id, status }`
    - `POST /analyze`: look up Need by ID (404 if missing), call `process_need_text` + `compute_urgency`, update Need record, return NLP result
    - `GET /prioritize`: query all needs with status != "fulfilled", return sorted by `urgency_score DESC` as list of `NeedResponse`
    - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.2, 2.3, 3.1, 3.3, 8.1, 8.2, 8.3_
  - [ ]* 6.2 Write property test: whitespace-only submissions are rejected
    - **Property 2: Whitespace-only submissions are rejected**
    - **Validates: Requirements 1.2**
    - Use Hypothesis `@given(st.text(alphabet=" \t\n", min_size=1))` to POST whitespace strings and assert HTTP 422 is returned and DB count is unchanged
    - `# Feature: live-need, Property 2: Whitespace-only submissions are rejected`
  - [ ]* 6.3 Write property test: prioritize returns needs in descending urgency order
    - **Property 7: Prioritize returns needs in descending urgency order**
    - **Validates: Requirements 3.3, 7.1**
    - Use Hypothesis to seed the DB with random needs having distinct urgency scores, call `GET /prioritize`, and assert each adjacent pair satisfies `scores[i] >= scores[i+1]`
    - `# Feature: live-need, Property 7: Prioritize returns needs in descending urgency order`

- [x] 7. Volunteer registration endpoint
  - [x] 7.1 Add `POST /register-volunteer` to `backend/routers/needs.py` (or a new `routers/volunteers.py`)
    - Accept name, email, role, skills (comma-separated), latitude, longitude
    - Return 409 if email already exists
    - Persist User record with `is_active=True`
    - _Requirements: 4.1, 4.3, 4.4_
  - [ ]* 7.2 Write unit test for duplicate email rejection
    - Register the same email twice and assert the second call returns HTTP 409
    - _Requirements: 4.3_

- [x] 8. Matching engine and /match endpoint
  - [x] 8.1 Implement `backend/matching_engine.py`
    - Implement `match_volunteers(need: Need, volunteers: list[User]) -> list[MatchResult]`
    - Skill score: +50 for primary skill match using `CATEGORY_TO_SKILL` map, +10 per additional relevant tag
    - Proximity score: Haversine distance, max +50 scaled to 0 at 100km; handle None lat/lon gracefully (score=0)
    - Exclude volunteers where `is_active=False` or who have an active Assignment
    - Sort results by `match_score` descending
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [x] 8.2 Implement `POST /match` in `backend/routers/matching.py`
    - Look up Need by ID (404 if missing)
    - Query all active volunteers with no active assignment
    - Call `match_volunteers`, return ranked list as `{ matches: [VolunteerMatchResult] }`
    - _Requirements: 5.1, 5.3, 5.4, 5.5, 8.4_
  - [ ]* 8.3 Write property test: matching excludes already-assigned volunteers
    - **Property 8: Matching excludes already-assigned volunteers**
    - **Validates: Requirements 5.4**
    - Use Hypothesis to create a need, a volunteer, assign the volunteer, then call `/match` for a second need and assert the assigned volunteer does not appear in results
    - `# Feature: live-need, Property 8: Matching excludes already-assigned volunteers`
  - [ ]* 8.4 Write property test: match scores are non-negative
    - **Property 9: Match scores are non-negative**
    - **Validates: Requirements 5.2**
    - Use Hypothesis to generate random volunteer/need combinations and assert all match scores >= 0
    - `# Feature: live-need, Property 9: Match scores are non-negative`

- [x] 9. Proof-of-Impact endpoint
  - [x] 9.1 Implement `POST /verify-impact` in `backend/routers/impact.py`
    - Validate that the Need exists (404), is not already "fulfilled" (409), and the volunteer is assigned to it (403)
    - Insert ImpactLog record with timestamp
    - Update Need status to "fulfilled" and Assignment status to "completed"
    - Return `{ impact_log_id, confirmed: true }`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.5_
  - [ ]* 9.2 Write property test: proof-of-impact round trip
    - **Property 10: Proof-of-impact round trip**
    - **Validates: Requirements 6.1, 6.2**
    - Use Hypothesis to create a need + volunteer + assignment, submit proof, then assert ImpactLog exists and Need status is "fulfilled"
    - `# Feature: live-need, Property 10: Proof-of-impact round trip`
  - [ ]* 9.3 Write property test: duplicate proof-of-impact is rejected
    - **Property 11: Duplicate proof-of-impact is rejected**
    - **Validates: Requirements 6.3**
    - Submit proof for a need, then submit again for the same need and assert HTTP 409 is returned and ImpactLog count is still 1
    - `# Feature: live-need, Property 11: Duplicate proof-of-impact is rejected`

- [ ] 10. Checkpoint – full backend API working
  - Ensure all tests pass, ask the user if questions arise.
  - Verify FastAPI `/docs` Swagger UI shows all 5 endpoints with correct schemas.

- [ ] 11. React frontend – core pages
  - [~] 11.1 Implement `frontend/src/pages/SubmitNeed.jsx`
    - Form with a textarea for need description, optional location text field, and a microphone button that uses the Web Speech API to populate the textarea via voice
    - On submit: POST to `/submit-need`, then immediately POST to `/analyze` with the returned need ID
    - Show success message with urgency score and category returned from `/analyze`
    - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.3_
  - [~] 11.2 Implement `frontend/src/pages/VolunteerReg.jsx`
    - Form with name, email, skill checkboxes (medical, logistics, counseling, education, construction, general), and lat/lon fields
    - POST to `/register-volunteer`, show success or conflict error
    - _Requirements: 4.1, 4.3, 4.4_
  - [~] 11.3 Implement `frontend/src/pages/Dashboard.jsx`
    - On load: GET `/prioritize` and display needs as `NeedCard` components sorted by urgency
    - Show `StatsBar` with total active needs, fulfilled needs, and volunteer count (add `GET /stats` endpoint to backend returning these three counts)
    - Each NeedCard has a "Find Volunteer" button that calls `POST /match` and shows the top match
    - Each NeedCard has a "Mark Fulfilled" button that calls `POST /verify-impact`
    - Auto-refresh every 30 seconds
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [~] 11.4 Implement `frontend/src/components/NeedCard.jsx`
    - Display: category badge (color-coded by urgency: red ≥70, orange 40–69, green <40), urgency score, raw text, location hint, status, and action buttons
    - _Requirements: 7.4_
  - [~] 11.5 Implement `frontend/src/components/StatsBar.jsx`
    - Three stat tiles: Active Needs, Fulfilled, Volunteers Registered
    - _Requirements: 7.3_

- [~] 12. Seed data script
  - Create `backend/seed.py` that inserts 8 sample needs (covering all 6 categories, varying urgency) and 5 volunteers with different skill sets and locations
  - Run `POST /analyze` for each seeded need to populate urgency scores
  - _Requirements: 3.1, 3.2, 5.1_

- [~] 13. Final checkpoint – full stack demo ready
  - Ensure all tests pass, ask the user if questions arise.
  - Run `python seed.py` and verify the dashboard shows color-coded need cards sorted by urgency.
  - Verify the complete flow: submit need → analyze → prioritize → match → verify impact.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests use Hypothesis with minimum 100 iterations per test
- Unit tests use pytest with FastAPI TestClient and an in-memory SQLite fixture
- The seed script is essential for a compelling judge demo
