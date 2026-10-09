# 🚆 SNCF Hackathon - Secure AI School Trip Planner

AI-powered school trip recommendation platform using trusted SNCF data, deterministic validation, and explainable AI.

---

## 📌 Overview

The goal of this project is to help teachers discover educational train-based trips in the Occitanie region.

Teachers can either:

- Fill out a structured search form
- Describe their trip in natural language

The system then:

1. Extracts requirements using AI
2. Validates feasibility using SNCF data
3. Filters invalid journeys
4. Ranks valid trip options
5. Explains recommendations transparently

The teacher always makes the final decision.

---

## 🎯 Problem Statement

Teachers often spend significant time:

- Searching destinations
- Checking train schedules
- Verifying accessibility
- Evaluating travel time
- Comparing costs

This platform automates those tasks while ensuring recommendations remain explainable and based on trusted SNCF information.

---

## ✨ Key Features

### 🤖 Natural Language Search

Example:

> "Je cherche une sortie scientifique pour 30 élèves depuis Toulouse, moins de 90 minutes de trajet, retour avant 18h et accessible PMR."

AI converts the request into structured constraints.

### ✅ Feasibility Validation

Every recommendation is validated against:

- Train availability
- Schedule constraints
- Group capacity
- Accessibility requirements
- Return journey availability
- Pricing rules

### 🏆 Recommendation Engine

Only feasible trips are ranked.

### 📊 Confidence Index

Transparent scoring based on:

- Reliability
- Accessibility
- Group suitability
- Journey simplicity
- Available historical metrics

### 🔍 Explainable Results

Every important value identifies its source:

| Type | Example |
|--------|----------|
| VERIFIED | SNCF schedule |
| CALCULATED | Trip score |
| AI-ASSISTED | Educational theme matching |

### 🔐 Secure Architecture

- Secrets remain server-side
- Input validation on every request
- Minimal personal data collection
- AI never performs transactions

---

# 🏗 Architecture

```text
Teacher
   |
 HTTPS
   |
   v
Frontend (Buddy)
   |
 REST / JSON
   |
   v
FastAPI Backend
   |
   +-- Validation
   +-- AI Parser
   +-- SNCF Data Service
   +-- Constraint Engine
   +-- Recommendation Engine
   +-- Confidence Engine
   +-- Explanation Engine
   |
   v
JSON Response
```

---

# 🔄 Request Flow

```text
Teacher Request
      |
      v
Natural Language / Form Input
      |
      v
AI Constraint Extraction
      |
      v
Structured Request
      |
      v
Constraint Engine
      |
      v
SNCF Data Validation
      |
      v
Recommendation Engine
      |
      v
Confidence Engine
      |
      v
Explanation Layer
      |
      v
Top Recommendations
```

---

# 🧠 AI Responsibilities

The AI is intentionally limited.

## AI CAN

- Understand teacher requests
- Extract constraints
- Identify educational themes
- Generate explanations
- Summarize recommendations

## AI CANNOT

- Purchase tickets
- Accept payments
- Modify SNCF data
- Determine train existence
- Override feasibility rules

---

# 🧩 Example Constraint Extraction

### User Input

```text
Je veux une sortie nature pour 28 élèves
depuis Toulouse avec moins de 90 minutes
de trajet.
```

### Structured Output

```json
{
  "origin": "Toulouse",
  "students": 28,
  "theme": "nature",
  "max_duration_minutes": 90
}
```

---

# 🚉 SNCF Data Layer

The application is built around a data adapter pattern.

Future SNCF datasets may include:

```text
trains.csv
destinations.csv
capacity.csv
punctuality.csv
feedback.csv
pricing.json
```

or

```text
SNCF APIs
GTFS Datasets
```

## SNCF Data Service

```python
get_stations()

find_trains()

get_train()

get_group_capacity()

get_reliability()

get_price_rules()
```

This adapter prevents the rest of the application from depending on dataset-specific formats.

---

# ✅ Constraint Engine

The Constraint Engine verifies every candidate trip.

```text
Train exists?
       |
Correct date?
       |
Group accepted?
       |
Within duration limit?
       |
Return train exists?
       |
Return before requested time?
       |
Accessibility compatible?
       |
Pricing rules valid?
       |
       v
   FEASIBLE
```

Trips failing any mandatory rule are rejected immediately.

---

# 🏆 Recommendation Engine

Only feasible trips are scored.

## Example Weighting

| Factor | Weight |
|----------|----------|
| Educational Match | 30% |
| Reliability | 20% |
| Journey Simplicity | 20% |
| Group Suitability | 15% |
| Cost | 10% |
| Accessibility | 5% |

Final weights will be adjusted after SNCF datasets are analyzed.

---

# 📊 Confidence Index

Example:

```text
Passenger Confidence Index

91 / 100

Reliability            94
Journey Simplicity     92
Group Suitability      90
Accessibility         100
Satisfaction           84
```

The platform never displays unexplained AI confidence.

Every score must be supported by available data.

---

# 📡 API Example

## Request

```http
POST /api/recommendations
```

```json
{
  "origin": "Toulouse",
  "date": "2026-11-20",
  "students": 28,
  "adults": 3,
  "theme": "science",
  "max_duration_minutes": 90,
  "return_before": "18:00",
  "accessibility_required": true
}
```

## Response

```json
{
  "recommendations": [
    {
      "trip_id": "TRIP-001",
      "destination": {
        "name": "Science Museum",
        "theme": "science",
        "educational_match": 96
      },
      "trip_score": 94,
      "confidence_score": 91,
      "accessible": true,
      "group_compatible": true,
      "reasons": [
        "Excellent educational match",
        "Journey below 90 minutes",
        "Compatible with group requirements",
        "Return before 18:00",
        "Accessibility requirement satisfied"
      ]
    }
  ]
}
```

---

# 🔍 Explainability Model

Every generated recommendation includes traceability.

| Information | Type | Source |
|-------------|--------|---------|
| Train schedule | VERIFIED | SNCF dataset |
| Capacity | VERIFIED | SNCF rules |
| Accessibility | VERIFIED | SNCF metadata |
| Estimated cost | CALCULATED | Pricing engine |
| Trip score | CALCULATED | Recommendation engine |
| Theme relevance | AI-ASSISTED | AI model |

---

# 🔐 Security Principles

## Rule 1 — Secrets Stay Backend-Side

✅ Correct

```text
Frontend
    |
    v
FastAPI
    |
    +--> LLM API
    +--> SNCF API
```

❌ Wrong

```text
Frontend
    |
    +--> API Keys
```

---

## Rule 2 — Data Minimization

Collected:

```json
{
  "students": 28,
  "age_group": "11-13",
  "accessibility_required": true
}
```

Never Collected:

- Student names
- Addresses
- Birth dates
- Student IDs
- Medical records
- Photos

---

## Rule 3 — Request Validation

```text
Browser Input
      |
      v
Pydantic Validation
      |
      v
Business Validation
      |
      v
Recommendation System
```

---

## Rule 4 — AI Has No Transaction Authority

Allowed:

- Understand requests
- Compare journeys
- Generate explanations

Not Allowed:

- Buy tickets
- Cancel reservations
- Process payments
- Modify SNCF data

---

# 🛡 Trust Levels

## LEVEL 1 — VERIFIED

- SNCF schedules
- Capacity data
- Pricing rules
- Destination metadata

## LEVEL 2 — CALCULATED

- Duration
- Estimated cost
- Trip score
- Confidence score

## LEVEL 3 — AI-ASSISTED

- Constraint extraction
- Educational relevance
- Human-readable explanations

---

# ⚠️ Failure Resilience

The demo must remain operational even if external services fail.

```text
SNCF Service
      |
API Available?
   /       \
 YES       NO
  |         |
  v         v
Live Data  Cached Data
```

Fallback datasets ensure uninterrupted demonstrations.

---

# 💾 Data Storage Strategy

### MVP

No database required.

```text
CSV
+
JSON
+
Pandas
+
FastAPI
```

### Future Enhancements

Add PostgreSQL for:

- Teacher accounts
- Saved trips
- Search history
- Feedback
- Reservation workflows

---

# 📁 Project Structure

```text
sncf-hackathon/
│
├── backend/
│   ├── app/
│   │
│   ├── api/
│   │
│   ├── models/
│   │
│   ├── services/
│   │   ├── sncf_service/
│   │   ├── ai_service/
│   │   ├── recommendation_service/
│   │   ├── confidence_service/
│   │   └── pricing_service/
│   │
│   ├── data/
│   │
│   ├── core/
│   │   ├── config/
│   │   └── security/
│   │
│   └── main.py
│
├── frontend/
│
├── tests/
│
├── .env.example
│
└── README.md
```

---

# 👥 Team Responsibilities

## Backend (You)

- SNCF dataset analysis
- FastAPI development
- Data adapters
- Constraint engine
- Recommendation engine
- Confidence scoring
- LLM integration
- Security implementation
- API documentation

## Frontend (Buddy)

- Search UX
- Natural language input
- Recommendation cards
- Map integration
- Trip comparison
- Confidence visualization
- Responsive design

---

# 🎬 Demo Scenario

### Teacher Request

```text
Sortie scientifique
30 élèves
Départ Toulouse
Moins de 1h30
Retour avant 18h
Accessible PMR
```

### System Workflow

```text
AI Constraint Extraction
          ↓
Constraint Validation
          ↓
SNCF Dataset Verification
          ↓
Top 3 Feasible Trips
          ↓
Scoring & Ranking
          ↓
Explainable Recommendation
```

### Result Example

```text
Trip #1 – Science Destination

Trip Score:       94 / 100
Confidence:       91 / 100

✓ Train Verified
✓ Group Compatible
✓ Accessibility Supported
✓ Return Before 18:00
✓ High Educational Relevance
✓ Reliable Route
```

---

# 🚀 Future Improvements

- Live SNCF APIs
- Interactive map routing
- Multi-day trips
- Teacher accounts
- Saved itineraries
- Reservation workflows
- Feedback-based recommendations
- AI-assisted trip comparison
- Real-time delay prediction

---

# 🎯 Core Principle

> AI understands the teacher.
>
> Trusted SNCF data describes reality.
>
> Deterministic code validates feasibility.
>
> The recommendation engine ranks valid options.
>
> The teacher makes the final decision.
