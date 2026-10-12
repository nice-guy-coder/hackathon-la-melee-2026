# AGENTS.md

## Repo layout

- Git root is `C:\hackathon-la-melee-2026`; **all project code lives under `sncf/`**.
  Commits: `design` (scaffold), `code` (working backend).
- `sncf/backend/` = working FastAPI app (implemented, 43 tests passing).
  `sncf/frontend/` = still an empty placeholder (`package.json` and `src/` are 0 bytes —
  no bundler, no framework; don't assume React/Vite).
  `sncf/docs/` = empty. `sncf/docker-compose.yml` = empty (no container workflow).
- `sncf/opencode.json` = repo-local OpenCode config; local Ollama provider
  (`qwen2.5-coder:14b` at `http://localhost:11434/v1`).

## Backend architecture (wiring, not obvious from filenames)

Request flow: `app/api/{search,compare,destinations,health}.py` → `SearchService`
(`app/services/search_service.py`, the facade) → parser → `ConstraintEngine` →
`RecommendationEngine` / `ConfidenceEngine` / `ExplanationEngine` → JSON.

- **Feasibility is deterministic, never AI.** `ConstraintEngine`
  (`app/engines/constraint_engine.py`) runs 8 spec objects (origin, date, duration, budget,
  return_before, accessibility, group capacity, transport); any failed check rejects the trip.
  AI/LLM only extracts constraints (`app/parsers/llm_parser.py`) and writes explanations.
- Two parsers behind a `RequestParser` protocol: `HeuristicParser` (regex, always available)
  and `OllamaParser` (server-side LLM, **falls back to heuristic on any error**).
  Selected by `Settings.llm_enabled` (`create_parser` in `llm_parser.py`).
- Data layer is an adapter registry (`app/data/factory.py`): `register_data_source("mock", ...)`
  builds repositories over JSON files in `app/mock/`. Add new sources by registering a builder,
  not by editing `SearchService`. `DataSourceError` → HTTP 503.
- App factory is `create_app(settings)` in `app/main.py`; tests build isolated apps from it.
- Every displayed value carries a `TrustLevel` (`VERIFIED` / `CALCULATED` / `AI-ASSISTED`)
  defined in `app/schemas/recommendation.py`. Preserve this in new output.

## Commands

Setup (system Python has no packages preinstalled):

```
pip install -r sncf/backend/requirements.txt
```

Tests — must run **from `sncf/backend/`** with **`python -m pytest`**:

```
cd sncf/backend
python -m pytest                                   # all tests (43 passing)
python -m pytest tests/test_parser.py -q           # one file
python -m pytest tests/test_search.py::test_valid_search_request   # one test
```

Gotchas (verified):

- Running from the repo root fails with `ModuleNotFoundError: No module named 'app'`;
  cwd must be `backend/`. `tests/conftest.py` provides fixtures (`client`,
  `settings`, `journey_factory`, `destination_factory`) but does **not** fix `sys.path`.
- Bare `pytest` is not on PATH here; `python -m pytest` from `backend/` is the reliable form.
- A `StarletteDeprecationWarning` about `httpx2` appears on every run; harmless, don't chase it.
- No lint, format, typecheck, codegen, CI, or pre-commit config exists anywhere (no `.github/`,
  no `pyproject.toml`). If you add tooling, there is no existing convention to follow.

## Configuration

- Settings are env-driven via `app/config.py` (`get_settings`, frozen dataclass,
  `lru_cache`). `.env` in `backend/` is loaded by `python-dotenv` (optional import).
  Template: `backend/.env.example`. Defaults: `DATA_SOURCE=mock`, `LLM_ENABLED=false`,
  docs on in development.
- Tests pass `Settings(...)` explicitly (see `conftest.py`); don't rely on env in tests.

## Conventions and traps

- **`sncf/README.md` is aspirational in places.** Trust code over README: real routes are
  `POST /api/search`, `POST /api/compare`, `GET /api/destinations`, `GET /api/health`
  (not `POST /api/recommendations`); there is no `core/` dir; tests live in
  `backend/tests/`, not a root `tests/`. The product principles in the README
  (secrets backend-only, AI never decides feasibility, trust tags, failure fallback)
  **do** match the code — keep them.
- `.gitignore` is **empty** and ~37 `__pycache__/*.pyc` files are committed. Running tests
  regenerates them, so `git status` shows churn after every run — never stage `.pyc` /
  `__pycache__`; add gitignore rules before committing generated files.
- `SearchRequest` requires **either `origin` or `query`** (model validator) and forbids
  extra fields (`extra="forbid"` — used on nearly every schema). Parsed LLM keys are
  filtered against `_ALLOWED_FIELDS` in `llm_parser.py`; extending extraction means
  updating that tuple plus `ExtractedConstraints`.
- LLM integration calls an OpenAI-compatible `/chat/completions` endpoint with
  `temperature=0` and extracts JSON from the reply (`_decode` strips code fences).
  Keys are allowlisted; invalid extraction falls back to heuristics and logs — never
  let LLM output reach the engines unvalidated.
- Frontend is unwritten: `frontend/package.json` and `frontend/src/services/api.js`
  are 0-byte placeholders. CORS already allows `localhost:5173` and `3000`.
