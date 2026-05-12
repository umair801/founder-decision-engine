# Founder Decision Engine

An AI-powered operating system for early-stage founders. Eliminates vague advice by enforcing structured decisions, numeric scoring, and actionable recommendations at every stage of the founder journey.

**Live API:** https://founder.datawebify.com/docs  
**Built by:** [Datawebify](https://datawebify.com)

---

## The Problem This Solves

Most founders waste 6-12 months building the wrong thing because they rely on:
- Unstructured advice from mentors and communities
- Gut-feel decisions with no scoring framework
- No enforced process between idea and execution

The Founder Decision Engine replaces this with a structured, AI-enforced pipeline that blocks progression until each stage meets a minimum quality threshold.

---

## System Architecture

```
User Input
    │
    ▼
FastAPI Backend (Railway)
    │
    ▼
LangGraph Orchestrator
    ├── Stage 1: Idea Clarity Agent         → Score 0-100 across 4 dimensions
    ├── Stage 2: Customer Discovery Agent   → Hard gate: blocks below score 60
    ├── Stage 3: Validation Agent           → Market validation scoring
    ├── Stage 4: Financial Reality Agent    → Build cost + break-even calculation
    └── Stage 5: Weekly Execution Agent     → 5-item structured action plan
    │
    ▼
Supervisor Agent (Claude API)
    │   Validates every output for vagueness
    │   Rejects "it depends" and "consider exploring"
    │
    ▼
Supabase (Session + Score Persistence)
    │
    ▼
Next.js Frontend (Vercel)
```

---

## Five Agent Modules

| Stage | Agent | Output | Gate |
|-------|-------|--------|------|
| 1 | Idea Clarity | Score across: problem clarity, target customer, differentiation, founder-market fit | None |
| 2 | Customer Discovery | 5 tailored interview questions + readiness score | Blocks below 60 |
| 3 | Validation | Market validation score across 4 dimensions + verdict | None |
| 4 | Financial Reality | Build cost, time to revenue, break-even + go/no-go | None |
| 5 | Weekly Execution | 5-item action plan with priority, time estimate, success criterion | None |

---

## Supervisor Agent

Every agent output passes through a two-layer vague output detection system:

- **Layer 1 (Rule-based):** Scans for banned phrases: "it depends", "consider exploring", "you might want to", "potentially", "could be"
- **Layer 2 (LLM-based):** Claude API validates that every recommendation is specific, numeric, and actionable

If either layer fails, the output is flagged and the agent is forced to regenerate.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph (multi-agent state machine) |
| LLMs | GPT-4o (agents) + Claude API (supervisor) |
| Backend | FastAPI + Python 3.12 |
| Schemas | Pydantic v2 (enforced structured output) |
| Database | Supabase (PostgreSQL) |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS |
| Deployment | Railway (backend) + Vercel (frontend) |
| Containerization | Docker |

---

## API Endpoints

### Run a founder stage
```
POST /api/founder/run
```

**Request body:**
```json
{
  "stage": "idea_clarity",
  "session_id": "optional-uuid",
  "idea_description": "AI tool that helps founders make structured decisions",
  "problem_statement": "Founders waste months building the wrong thing"
}
```

**Response:**
```json
{
  "session_id": "3834f394-2fc6-41a9-aaf2-deee4570c540",
  "stage": "idea_clarity",
  "output": {
    "scores": {
      "problem_clarity": 12,
      "target_customer_specificity": 8,
      "differentiation": 10,
      "founder_market_fit": 8
    },
    "total_score": 38,
    "verdict": "weak",
    "gap_analysis": ["No specific target customer defined", "Differentiation unclear vs existing tools"],
    "required_next_action": "Define a specific target customer segment with clear characteristics"
  },
  "supervisor_validation": {
    "passed": true,
    "vague_outputs_found": [],
    "missing_fields": []
  },
  "next_stage": "customer_discovery",
  "blocked": false
}
```

### List all stages
```
GET /api/stages
```

### Health check
```
GET /health
```

---

## Stage Gate Logic

```
Idea Clarity → Customer Discovery → Validation → Financial Reality → Weekly Execution
                       ↑
               HARD GATE (score < 60)
               Returns required actions
               Blocks progression
```

Customer discovery is the only mandatory gate. Founders cannot reach the validation stage without achieving a discovery readiness score of 60 or above.

---

## Project Structure

```
backend/
  app/
    agents/
      idea_clarity_agent.py
      customer_discovery_agent.py
      validation_agent.py
      financial_reality_agent.py
      weekly_execution_agent.py
      supervisor_agent.py
      orchestrator.py
    prompts/
      idea_clarity.py
      customer_discovery.py
      validation.py
      financial_reality.py
      weekly_execution.py
    schemas/
      models.py
    tools/
      llm.py
      supabase_client.py
      model_router.py
      memory.py
      error_handler.py
    main.py
  .env
  requirements.txt
  Dockerfile
database/
  schema.sql
frontend/
railway.toml
```

---

## Local Setup

**1. Clone the repository:**
```bash
git clone https://github.com/umair801/founder-decision-engine.git
cd founder-decision-engine
```

**2. Create virtual environment:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment:**
```bash
# Create backend/.env with the following keys:
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

**5. Run the backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**6. Open API docs:**
```
http://localhost:8001/docs
```

---

## Deployment

| Service | Platform | URL |
|---------|----------|-----|
| Backend API | Railway | https://founder.datawebify.com |
| Frontend | Vercel | https://founder.datawebify.com |
| API Docs | Railway | https://founder.datawebify.com/docs |
| Database | Supabase | agai_portfolio project |

---

## Portfolio Context

This project targets the intersection of three high-demand Upwork categories:

- **Prompt engineering + LLM workflow architecture** — modular system prompt library, one prompt file per agent module
- **Structured AI outputs** — Pydantic-enforced JSON schemas, numeric scoring, zero narrative paragraphs
- **Agentic AI systems** — LangGraph orchestration, multi-agent routing, supervisor validation layer

**Live demo:** https://founder.datawebify.com  
**Full portfolio:** https://datawebify.com  
**GitHub:** https://github.com/umair801

---

## License

MIT License. Built by [Datawebify](https://datawebify.com).
