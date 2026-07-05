# Christmas Menu Generator - AI Coding Agent Instructions

## Project Overview

**Christmas Menu Generator** is a full-stack AI application that generates personalized Christmas menus using multi-agent orchestration with **Datapizza AI** and **Google Gemini 2.5 Flash**. It's a Python backend (FastAPI) + React/TypeScript frontend that demonstrates enterprise patterns for structured AI responses and agent collaboration.

**Key Stack:** Python 3.12 + FastAPI | Datapizza AI 0.0.9 | Google Gemini | React 18 + TypeScript + Vite

---

## Architecture & Data Flow

### Three-Agent Orchestration Pattern

The system uses **three specialized agents** that collaborate:

1. **Menu Agent** (`backend/agents/menu_agent.py`): Chef/planner that generates courses based on user preferences, cuisines, dietary restrictions, and budget
2. **Recipe Agent** (`backend/agents/recipe_agent.py`): Culinary expert that details each course with full ingredient lists, cooking methods, timing
3. **Aggregation Agent** (`backend/agents/aggregation_agent.py`): Organizer that consolidates ingredients into shopping lists (by category), creates prep timelines (2 days before → day-of)

**Data Flow:**
```
UserInput (frontend) 
  → FastAPI endpoint 
  → MenuService orchestrates agents 
  → structured_generation.py handles Gemini calls 
  → MenuOutput (menu + shopping list + timeline) 
  → Frontend displays in tabs
```

### Critical: Gemini API Limitations on Structured Responses

⚠️ **Google Gemini does NOT support `additionalProperties` in JSON schemas**. This affects how we generate complex outputs:

- **Complex models** (MenuOutput): Use `invoke()` method with manual JSON parsing in `structured_generation.py`
- **Simple models** (Recipe, Course): Use `structured_response()` method safely
- See `backend/services/structured_generation.py` lines 1-40 for detailed explanation and the fallback strategy

This pattern is non-obvious and critical to understand before modifying generation code.

---

## Key Files & Responsibilities

### Backend Structure

| Layer | Key Files | Purpose |
|-------|-----------|---------|
| **Models** | `backend/models/{input,output,menu}_models.py` | 15+ Pydantic models defining request/response contracts; validators enforce rules (no overlapping preferred/avoided ingredients) |
| **Agents** | `backend/agents/{menu,recipe,aggregation}_agent.py` | Datapizza Agent instances with specialized system prompts; each has memory and tool access |
| **Tools** | `backend/tools/{ingredient,calculation,aggregation}_tools.py` | Custom functions agents call: ingredient validation, portion calculations, ingredient aggregation by category |
| **Structured Gen** | `backend/services/structured_generation.py` | Core: calls Google client, parses JSON, implements fallback strategy for Gemini limitations |
| **Menu Service** | `backend/services/menu_service.py` | Orchestrates agent collaboration, manages in-memory menu storage, validates output |
| **API Routes** | `backend/api/menu_routes.py` | FastAPI endpoints: `/generate`, `/regenerate-course/{course_type}`, CORS-enabled for frontend |
| **Config** | `backend/config.py` | Creates GoogleClient instances with API key from `.env` |

### Frontend Structure

| Component | Key Files | Purpose |
|-----------|-----------|---------|
| **API Client** | `frontend/src/services/api.ts` | Axios wrapper for backend endpoints, health check |
| **Types** | `frontend/src/types/index.ts` | TypeScript interfaces mirroring Pydantic models |
| **Main App** | `frontend/src/App.tsx` | Form state management, tab navigation (Menu/Shopping/Timeline views) |

---

## Developer Workflows

### Setup
```powershell
# Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create .env with: GOOGLE_API_KEY=your_key, GEMINI_MODEL=gemini-2.5-flash

# Frontend
cd frontend
npm install
```

### Run Locally
```powershell
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev  # Vite dev server, default port 5173
```

### Testing
```powershell
# Backend unit tests (agents, models, tools)
pytest backend/test_*.py -v

# Frontend: No formal test suite yet
```

### Key Commands Not Obvious from Files
- **Check backend API docs:** Navigate to `http://localhost:8000/docs` (Swagger UI auto-generated)
- **Frontend build:** `npm run build` outputs to `frontend/dist/`
- **Type check frontend:** Uses implicit TypeScript (no explicit `tsc` command in package.json, relies on Vite)

---

## Project-Specific Patterns & Conventions

### 1. Prompt Engineering for Italian-Centric Menus
All system prompts (agents + tools) are in **Italian** because the domain is Italian/Mediterranean Christmas menus. Agent outputs also default to Italian. When extending, maintain this language for system prompts unless user input specifies otherwise.

### 2. Pydantic Field Validators as Business Rules
```python
# Example: input_models.py validates no ingredient overlaps
@field_validator('avoided_ingredients')
def check_no_overlap(cls, v, info):
    preferred = info.data.get('preferred_ingredients', [])
    overlap = set(v) & set(preferred)
    if overlap:
        raise ValueError(f"Overlap: {overlap}")
```
**Key insight:** Validation happens at model instantiation, not at API layer. Always validate in models first.

### 3. Agent System Prompts Define Behavior
Agent competencies are declared in system prompts (e.g., `MENU_PLANNER_SYSTEM_PROMPT`), not in code logic. To change agent behavior, modify the system prompt, not the agent instantiation code.

### 4. Tools Are Agent Actions, Not Independent Functions
Tools in `backend/tools/` are designed to be called by agents via Datapizza framework. They return structured data agents can reason about. See `backend/agents/menu_agent.py` for how tools are registered.

### 5. In-Memory Storage for Development
`backend/services/menu_service.py` uses a simple Python dict (`menu_store`) for storing generated menus. **This is NOT production-ready**—data is lost on server restart. For persistence, implement a database backend (notes suggest MongoDB or PostgreSQL).

### 6. Frontend Tab Architecture
App.tsx manages three views via `activeTab` state: `menu` (courses/recipes), `shopping` (ingredients by category), `timeline` (prep schedule). State passed to child components via props (no component composition shown, but structure is flat).

---

## Integration Points & Gotchas

### Google Gemini API Rate Limits
Free tier: **15 requests/minute, 1500/day**. Menu generation makes 2-3 Gemini calls (menu agent → recipe agent → aggregation). Long menus or frequent tests hit limits quickly. Solution: Add request queuing or use slower polling in frontend.

### CORS Configuration
Backend (`backend/main.py`) enables CORS for `http://localhost:5173` (frontend dev server). If frontend runs on different port, update `CORS` middleware origins list.

### Environment Variable: DATAPIZZA_AGENT_LOG_LEVEL
Set in `backend/main.py` startup. Defaults to `INFO`. For debugging agents, set to `DEBUG` (verbose output). Toggle via `.env` or environment.

### Async Pattern in Menu Service
`MenuService.generate_menu()` is async but calls synchronous `generate_menu_structured()` via `asyncio.run_in_executor()` to avoid blocking. If refactoring, maintain this pattern to keep API responsive.

---

## Common Extension Points

**Adding a new agent?**
1. Create file `backend/agents/your_agent.py` with system prompt and tools
2. Register in `MenuService.generate_menu()` to call your agent in the orchestration chain
3. Update output models to include agent's output

**Adding a dietary restriction?**
1. Add to `DietaryRestriction` enum in `backend/models/input_models.py`
2. Update Menu Agent system prompt to explain how to handle it
3. Frontend already iterates over enum values, no UI changes needed

**Changing menu structure?** (e.g., more courses)
1. Modify `MenuCourses` model in `backend/models/menu_models.py`
2. Update agent system prompts to reflect new structure
3. Update frontend tab view to display new course type

---

## Testing Strategy (Incomplete)

Project has unit test files (`backend/test_*.py`) but these are **sparse and under-utilized**. 
- **test_models.py:** Validates Pydantic models
- **test_tools.py:** Tests agent tools in isolation
- **test_agents.py:** Tests agent creation (not orchestration)
- **test_api.py:** Tests endpoints (minimal)

**Missing:** E2E tests for full menu generation, integration tests for agent collaboration. Tests would reduce risk when changing system prompts or tool signatures.

---

## Notes for AI Agents

When working on this codebase:
1. Always check `structured_generation.py` first—it's the most complex layer and contains workarounds for Gemini limitations
2. Validate new code against test files to maintain consistency
3. Italian prompts are intentional; don't anglicize without explicit request
4. In-memory storage is a known limitation; document it if adding features that depend on persistence
5. Check `.env` requirements before running—missing GOOGLE_API_KEY causes graceful startup failures (prints warnings)
6. Frontend tabs are managed via simple state; no router framework (no URL-based navigation)
