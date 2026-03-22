# AI Task Assignment Service — Python Microservice
 
Part of a larger **AI-based task assignment system** built for a Jira-like desktop application. This microservice is responsible for the entire AI/scoring layer — it receives a task and a list of workers, computes a match score for each worker, and returns a ranked list with explainable breakdowns.
 
The Java desktop application handles the UI, database, and business logic. This service does one thing: **score and rank workers**.
 
---
 
## How It Works
 
When a manager clicks "Suggest Worker" in the desktop app, the Java application sends a request to this service with the task description, required skills, and worker data. The service then:
 
1. Converts the task description into a **384-dimensional sentence embedding** using a pretrained transformer model (`all-MiniLM-L6-v2`)
2. Computes **semantic similarity** between the new task and each worker's past completed tasks using cosine similarity
3. Computes **skill overlap** between required task skills and worker skills
4. Computes a **workload penalty** based on the worker's current active tasks
5. Combines all components into a **final weighted score**
6. Returns a **ranked list** with a full breakdown and human-readable explanation for each worker
 
---
 
## Scoring Formula
 
```
final_score = 0.5 × text_similarity + 0.3 × skill_overlap + 0.2 × workload_score
```
 
All components are normalized between 0 and 1.
 
| Component | Weight | Description |
|---|---|---|
| `text_similarity` | 50% | Cosine similarity between new task and worker's past tasks |
| `skill_overlap` | 30% | Ratio of required skills the worker possesses |
| `workload_score` | 20% | Penalty for workers with many active tasks |
 
---
 
## Explainability
 
Every recommendation includes two layers of explanation — the system never produces unexplained scores.
 
**1. Human-readable explanation string**
A plain English summary generated from predefined templates driven by the actual score components. No AI text generation — every sentence is directly tied to a measurable value.
 
Example: `"Strong match. Their past work is very similar to this task ("Implemented REST API with JWT auth in FastAPI"). They have all required skills (Python, FastAPI, PostgreSQL). Their current workload is low (1 active tasks)."`
 
The verdict is determined by the final score:
| Score | Verdict |
|---|---|
| ≥ 0.8 | Strong match |
| ≥ 0.6 | Good match |
| ≥ 0.4 | Partial match |
| < 0.4 | Weak match |
 
**2. Structured breakdown**
All individual score components are returned so the frontend can display them however it likes.
 
Example full response:
 
```json
{
  "worker_id": 1,
  "worker_name": "Alice",
  "final_score": 0.9382,
  "explanation": "Strong match. Their past work is very similar to this task (\"Implemented REST API with JWT auth in FastAPI\"). They have all required skills (Python, FastAPI, PostgreSQL). Their current workload is low (1 active tasks).",
  "breakdown": {
    "text_similarity": 0.9564,
    "most_similar_task": "Implemented REST API with JWT auth in FastAPI",
    "skill_overlap": 1.0,
    "matched_skills": ["Python", "FastAPI", "PostgreSQL"],
    "missing_skills": [],
    "match_ratio": "3/3",
    "workload_score": 0.8,
    "active_tasks": 1
  }
}
```
 
---
 
## Tech Stack
 
- **Python 3.11**
- **FastAPI** — REST API framework
- **sentence-transformers** — pretrained transformer model for text embeddings
- **NumPy** — vector math and cosine similarity
- **Docker + Docker Compose** — containerized deployment
 
---
 
## Project Structure
 
```
ai-service/
├── embeddings.py       # Loads transformer model, converts text → vectors
├── similarity.py       # Cosine similarity, task-to-task comparison
├── scorers.py          # Skill overlap and workload scoring functions
├── scoring_engine.py   # Combines all components into final score and ranking
├── schemas.py          # Pydantic request/response models
├── main.py             # FastAPI app and endpoint definitions
├── requirements.txt    # Python dependencies
└── Dockerfile          # Container definition
```
 
---
 
## Running Locally
 
### Prerequisites
- Docker Desktop installed and running
 
### Start the service
 
```bash
docker-compose up --build
```
 
The service will be available at `http://localhost:8000`.
 
Interactive API docs (Swagger UI): `http://localhost:8000/docs`
 
---
 
## API
 
### `POST /suggest`
 
Accepts a task and list of workers, returns them ranked by match score.
 
**Request body:**
```json
{
  "description": "Build a REST API with JWT authentication using FastAPI",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "workers": [
    {
      "id": 1,
      "name": "Alice",
      "skills": ["Python", "FastAPI", "PostgreSQL"],
      "active_tasks": 1,
      "max_tasks": 5,
      "past_tasks": [
        {"description": "Implemented REST API with JWT auth in FastAPI"}
      ]
    }
  ]
}
```
 
**Response:**
```json
{
  "ranked_workers": [
    {
      "worker_id": 1,
      "worker_name": "Alice",
      "final_score": 0.9382,
      "explanation": "Strong match. Their past work is very similar to this task...",
      "breakdown": { ... }
    }
  ]
}
```
 
---
 
## Architecture
 
This service is one part of a larger system:
 
```
┌──────────────────────┐        HTTP localhost:8000       ┌─────────────────────┐
│  Java Desktop App    │  ──── POST /suggest ──────────▶  │  Python AI Service  │
│  + PostgreSQL DB     │  ◀─── ranked workers ──────────  │  (this repo)        │
└──────────────────────┘                                  └─────────────────────┘
```
 
The Java application is responsible for all data persistence — workers, tasks, skills, and assignment history are stored in PostgreSQL. The Python service is **stateless** — it receives all necessary data in the request and returns scores without touching any database.
 
