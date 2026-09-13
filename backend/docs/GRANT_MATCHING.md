# Grant Matching Workflow — Milestone 2

## Files Created

| File | Purpose |
|------|---------|
| `backend/app/models/grant.py` | SQLAlchemy ORM model for the `grants` table |
| `backend/app/schemas/grant.py` | Pydantic request/response schemas |
| `backend/app/services/grant_matching.py` | Deterministic rule-based matching algorithm |
| `backend/app/routes/grants.py` | FastAPI router — CRUD + matching endpoints |
| `backend/app/routes/__init__.py` | Package marker |
| `backend/app/schemas/__init__.py` | Package marker |
| `backend/app/services/__init__.py` | Package marker |
| `backend/scripts/seed_grants.py` | One-time seed script (10 sample grants) |

## Files Modified

| File | Change |
|------|--------|
| `backend/app/main.py` | Added `Grant` model import, `grants_router` import, `app.include_router(grants_router)` |

---

## Database Changes

- New table: `grants` created via `Base.metadata.create_all()` (same pattern as existing tables)
- 10 sample grant rows inserted via `scripts/seed_grants.py`
- No existing tables modified

### grants table schema

```sql
CREATE TABLE grants (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    grant_name       VARCHAR(500) NOT NULL,
    funding_organization VARCHAR(255) NOT NULL,
    description      TEXT,
    research_area    VARCHAR(255),
    keywords         TEXT,          -- comma-separated
    eligibility      TEXT,
    country          VARCHAR(100),
    funding_amount   DECIMAL(15,2),
    deadline         DATE,
    application_url  VARCHAR(500),
    status           VARCHAR(50) DEFAULT 'open',
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/grants/` | List all grants |
| GET | `/grants/{id}` | Get grant by ID |
| POST | `/grants/` | Create a new grant |
| PUT | `/grants/{id}` | Update a grant |
| DELETE | `/grants/{id}` | Delete a grant |
| POST | `/grants/match` | Match researcher profile against grants |

---

## Grant Matching Algorithm

### Scoring Weights (total = 100)

| Component | Weight | Logic |
|-----------|--------|-------|
| Research area | 30 | Exact match = 30, partial/substring = 21, word overlap = proportional |
| Keyword overlap | 30 | Ratio of researcher keywords found in grant keywords × 30 |
| Eligibility | 20 | Substring match = 20, word overlap = proportional × 0.6 |
| Country | 10 | Exact match = 10; "International"/"Global" grants = 10 for any country |
| Description | 10 | Ratio of researcher keywords found in grant description × 10 |

Weights are defined as constants at the top of `grant_matching.py` and can be changed without touching logic.

---

## Starting the Backend

```powershell
# From the project root
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Server runs at: `http://127.0.0.1:8000`  
Swagger UI: `http://127.0.0.1:8000/docs`

---

## Seeding Sample Data

```powershell
# From backend/ directory (run once)
python -m scripts.seed_grants
```

Safe to re-run — skips if grants already exist.

---

## Example: POST /grants/match

**Request:**
```json
{
  "research_area": "Artificial Intelligence",
  "keywords": ["Machine Learning", "Deep Learning", "Computer Vision"],
  "country": "India",
  "eligibility": "University Researcher"
}
```

**Response (truncated to top 2):**
```json
{
  "matches": [
    {
      "grant_id": 1,
      "grant_name": "AI Research Excellence Grant",
      "organization": "National Science Foundation (Sample)",
      "match_score": 86,
      "matching_reasons": [
        "Research area matches exactly",
        "'Machine Learning' keyword matched",
        "'Deep Learning' keyword matched",
        "Eligibility criteria matched",
        "Country eligibility matched",
        "Description mentions: Machine Learning, Deep Learning"
      ],
      "deadline": "2026-06-30",
      "funding_amount": "150000.00",
      "application_url": "https://example.org/ai-research-grant"
    },
    {
      "grant_id": 10,
      "grant_name": "Edge Computing and IoT Research Grant",
      "organization": "IoT Research Alliance (Sample)",
      "match_score": 63,
      "matching_reasons": [
        "'Machine Learning' keyword matched",
        "'Deep Learning' keyword matched",
        "'Computer Vision' keyword matched",
        "Eligibility criteria matched",
        "Country eligibility matched",
        "Description mentions: Machine Learning"
      ],
      "deadline": "2026-08-15",
      "funding_amount": "70000.00",
      "application_url": "https://example.org/edge-iot-grant"
    }
  ]
}
```

---

## Validation Rules

| Rule | Behaviour |
|------|-----------|
| `keywords` empty list | 422 — "keywords list must not be empty" |
| `funding_amount` negative | 422 — "funding_amount must be non-negative" |
| `deadline` in the past | 422 — "deadline cannot be in the past" |
| Grant ID not found | 404 — "Grant not found" |
| Missing required fields | 422 — FastAPI/Pydantic validation error |

---

## Sample Grants Included

| # | Grant Name | Research Area | Country | Amount |
|---|-----------|---------------|---------|--------|
| 1 | AI Research Excellence Grant | Artificial Intelligence | India | $150,000 |
| 2 | Computer Vision Innovation Fund | Computer Vision | India | $80,000 |
| 3 | Healthcare AI Research Program | Healthcare AI | International | $200,000 |
| 4 | Climate Technology Research Grant | Climate Technology | International | $120,000 |
| 5 | Robotics and Autonomous Systems Fellowship | Robotics | India | $60,000 |
| 6 | Natural Language Processing Research Award | NLP | India | $90,000 |
| 7 | Cybersecurity and AI Defense Grant | Cybersecurity | India | $175,000 |
| 8 | Data Science and Big Data Innovation Grant | Data Science | International | $100,000 |
| 9 | Biomedical Engineering Research Fund | Biomedical Engineering | International | $130,000 |
| 10 | Edge Computing and IoT Research Grant | Edge Computing | India | $70,000 |

> **Note:** All grants are SAMPLE/FICTIONAL data for testing purposes only.
