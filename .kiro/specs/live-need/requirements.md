# Requirements Document

## Introduction

LiveNeed is an AI-powered smart resource allocation platform designed for community organizations and NGOs. It collects community needs via text or voice input, uses NLP to extract structured information (location, need type, urgency), scores and prioritizes requests, matches available volunteers based on skills and proximity, and tracks completed tasks through a Proof-of-Impact system. The platform provides a dashboard for real-time visualization of needs, assignments, and impact.

## Glossary

- **Need**: A community request submitted by a reporter describing a resource gap or urgent situation
- **Reporter**: A community member or NGO staff member who submits a need
- **Volunteer**: A registered user with skills and a location who can be assigned to fulfill needs
- **Urgency_Score**: A numeric value (0–100) representing the priority of a need, computed by the NLP module
- **Assignment**: A record linking a Volunteer to a Need for fulfillment
- **Impact_Log**: A record confirming that a Need has been fulfilled, including evidence
- **NLP_Module**: The backend AI component responsible for extracting entities and computing urgency from raw need text
- **Matching_Engine**: The backend component that selects the best-fit Volunteer for a given Need
- **Dashboard**: The frontend visualization interface showing needs, assignments, and impact metrics
- **Proof_of_Impact**: The process and data model for verifying and recording that a Need was fulfilled

---

## Requirements

### Requirement 1: Submit Community Needs

**User Story:** As a reporter, I want to submit a community need via text or voice, so that the platform can process and prioritize it for volunteer response.

#### Acceptance Criteria

1. WHEN a reporter submits a need with a non-empty text description, THE System SHALL accept the submission and return a unique need ID
2. WHEN a reporter submits a need with an empty or whitespace-only description, THE System SHALL reject the submission and return a descriptive validation error
3. WHEN a reporter submits a need, THE System SHALL record the submission timestamp, raw text, and optional location metadata
4. WHERE voice input is provided, THE System SHALL transcribe the audio to text before processing
5. IF the submission payload is malformed or missing required fields, THEN THE System SHALL return an HTTP 422 error with field-level details

---

### Requirement 2: NLP Processing of Need Descriptions

**User Story:** As a platform operator, I want the system to automatically extract structured information from raw need text, so that needs can be categorized and prioritized without manual review.

#### Acceptance Criteria

1. WHEN a need text is submitted for analysis, THE NLP_Module SHALL extract at least one of: location, need type, or urgency indicators from the text
2. WHEN the NLP_Module processes a need, THE NLP_Module SHALL classify the need into one of the predefined categories: food, medical, shelter, safety, education, or other
3. WHEN the NLP_Module processes a need, THE NLP_Module SHALL return a structured JSON object containing extracted entities, category, and urgency signals
4. IF the NLP_Module cannot extract any entities from the text, THEN THE NLP_Module SHALL return a default structured response with null entity fields and category set to "other"
5. THE NLP_Module SHALL process a need text and return a response within 5 seconds under normal load

---

### Requirement 3: Urgency Scoring

**User Story:** As a platform operator, I want each need to receive an urgency score, so that the most critical needs are surfaced and addressed first.

#### Acceptance Criteria

1. WHEN a need is analyzed, THE System SHALL assign an Urgency_Score between 0 and 100 inclusive
2. WHEN computing an Urgency_Score, THE System SHALL consider keyword signals (e.g., "emergency", "critical", "urgent"), need category, and recency of submission
3. WHEN two needs are compared, THE System SHALL rank the need with the higher Urgency_Score as higher priority
4. IF a need contains explicit emergency keywords, THEN THE System SHALL assign an Urgency_Score of at least 70
5. THE System SHALL recompute the Urgency_Score if the need description is updated

---

### Requirement 4: Volunteer Registration and Profile Management

**User Story:** As a volunteer, I want to register with my skills and location, so that I can be matched to needs I am qualified and available to fulfill.

#### Acceptance Criteria

1. WHEN a volunteer registers, THE System SHALL store the volunteer's name, contact information, skill tags, and geographic location
2. WHEN a volunteer updates their profile, THE System SHALL persist the updated information and use it in subsequent matching operations
3. IF a volunteer attempts to register with an email address already in use, THEN THE System SHALL return a conflict error and not create a duplicate record
4. THE System SHALL support at least the following skill tags: medical, logistics, counseling, education, construction, general
5. WHEN a volunteer is deactivated, THE System SHALL exclude that volunteer from all future matching operations

---

### Requirement 5: Volunteer Matching

**User Story:** As a platform operator, I want the system to automatically match volunteers to needs based on skills and proximity, so that the right help reaches the right place quickly.

#### Acceptance Criteria

1. WHEN a match request is made for a need, THE Matching_Engine SHALL return a ranked list of available volunteers ordered by match score
2. WHEN computing a match score, THE Matching_Engine SHALL consider skill overlap between the need category and volunteer skill tags, and geographic proximity
3. WHEN no volunteers match the required skill for a need, THE Matching_Engine SHALL return an empty list and a descriptive message
4. THE Matching_Engine SHALL exclude volunteers who are already assigned to an active need from match results
5. WHEN a volunteer is matched and assigned to a need, THE System SHALL create an Assignment record linking the volunteer to the need

---

### Requirement 6: Proof-of-Impact Verification

**User Story:** As a platform operator, I want volunteers to submit proof that a need was fulfilled, so that the platform can track real-world impact and build accountability.

#### Acceptance Criteria

1. WHEN a volunteer submits a proof-of-impact for an assignment, THE System SHALL record the submission with a timestamp, volunteer ID, need ID, and optional notes or photo URL
2. WHEN a proof-of-impact is submitted, THE System SHALL update the associated Need status to "fulfilled"
3. IF a proof-of-impact is submitted for a need that is already marked "fulfilled", THEN THE System SHALL return an error indicating the need is already closed
4. IF a proof-of-impact is submitted by a volunteer not assigned to the need, THEN THE System SHALL reject the submission with an authorization error
5. THE System SHALL maintain an immutable Impact_Log entry for every accepted proof-of-impact submission

---

### Requirement 7: Prioritized Needs Dashboard

**User Story:** As an NGO coordinator, I want to view all active needs sorted by urgency, so that I can monitor the situation and make informed allocation decisions.

#### Acceptance Criteria

1. WHEN the dashboard is loaded, THE Dashboard SHALL display all active needs sorted by Urgency_Score in descending order
2. WHEN a need is fulfilled, THE Dashboard SHALL remove it from the active needs list and move it to a completed section
3. WHEN the dashboard is loaded, THE Dashboard SHALL display summary statistics: total active needs, total fulfilled needs, and total volunteers registered
4. WHEN a need is selected, THE Dashboard SHALL display the full need details including extracted entities, urgency score, category, and current assignment status
5. THE Dashboard SHALL reflect need status changes within 30 seconds of the change occurring

---

### Requirement 8: API Layer

**User Story:** As a developer integrating with LiveNeed, I want a well-defined REST API, so that I can build clients and integrations reliably.

#### Acceptance Criteria

1. THE System SHALL expose a POST /submit-need endpoint that accepts a need description and returns a need ID and status
2. THE System SHALL expose a POST /analyze endpoint that accepts a need ID and returns extracted entities, category, and urgency score
3. THE System SHALL expose a GET /prioritize endpoint that returns all active needs sorted by Urgency_Score descending
4. THE System SHALL expose a POST /match endpoint that accepts a need ID and returns a ranked list of matching volunteers
5. THE System SHALL expose a POST /verify-impact endpoint that accepts a volunteer ID, need ID, and proof details, and returns a confirmation
6. IF any API endpoint receives a request with an invalid or missing authentication token, THEN THE System SHALL return an HTTP 401 response

---

### Requirement 9: Data Persistence

**User Story:** As a platform operator, I want all platform data to be persisted reliably, so that no need, assignment, or impact record is lost between sessions.

#### Acceptance Criteria

1. THE System SHALL persist all Need records to a SQLite database on creation and update
2. THE System SHALL persist all Volunteer records to a SQLite database on creation and update
3. THE System SHALL persist all Assignment records to a SQLite database on creation
4. THE System SHALL persist all Impact_Log records to a SQLite database on creation
5. WHEN the backend service restarts, THE System SHALL restore all previously persisted records without data loss
