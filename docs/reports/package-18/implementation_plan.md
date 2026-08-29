# Package 18 — Deployment Architecture & Implementation Plan

## 1. Executive Summary

Package 18 defines the concrete deployment architecture for the RecoverAI MVP. The forensic inspection reveals a functional but fragmented startup story: the backend has a proper entrypoint (`uvicorn recoverai.api.main:app`), the frontend has Vite dev and build scripts, and n8n has a Docker Compose sidecar — but there is no unified orchestration script, no `.env.example` covering P17 security variables, no frontend environment example, several broken n8n workflow expressions, and no llama.cpp/Qwen3 integration in the codebase. P18 will create the unified startup/shutdown scripts, fix configuration gaps, document the exact deployment procedure, and establish the failure/recovery matrix — all on native Windows.

## 2. Package Scope

P18 covers:
- Unified startup/shutdown scripts (PowerShell)
- Environment configuration completeness (`.env.example` update, `frontend/.env.example`)
- n8n workflow expression fix (`{{ .N8N_API_KEY }}` → `{{ $env.N8N_API_KEY }}`)
- n8n compose.yaml `N8N_API_KEY` environment variable injection
- Deployment documentation
- Health/readiness verification scripts
- Failure matrix documentation
- llama.cpp/Qwen3-8B integration gap documentation

P18 does NOT cover:
- Business logic changes
- UI redesign
- New authentication architecture
- Database redesign
- Production cloud migration
- P19/P20 functionality

## 3. Frozen Constraints

- **P01–P17**: All frozen. No domain, policy, state machine, persistence, integration, frontend component, page, or security architecture changes.
- **Warm Premium UI**: Frozen.
- **Docker-free core**: The backend, frontend, SQLite, MCP, and LLM Gateway run natively on Windows. Docker is used ONLY for n8n as a sidecar.
- **No scope creep**: P19/P20 not started.

## 4. Repository Reality Assessment

### Backend
- **Entrypoint**: `recoverai/api/main.py` defines `app = FastAPI(...)`. Started via `uvicorn recoverai.api.main:app --port 8000`.
- **Bootstrap script**: `scripts/start.ps1` runs `uv run python -m recoverai.main` which is the P01 minimal bootstrap (NOT the FastAPI server). This is a **deployment gap**.
- **Configuration**: `recoverai/config.py` loads from `.env` via `pydantic-settings`. All credentials have safe defaults.
- **Database**: SQLite at `sqlite:///recoverai.db` (WAL mode, foreign keys enforced). Migrations run automatically on `AppContainer.__init__()`.
- **MCP**: Embedded inside the FastAPI process. Not a separate service. Exposed at `POST /mcp/execute`.
- **LLM Gateway**: Embedded inside the FastAPI process. Uses external cloud APIs (Gemini, Groq, HuggingFace) via `urllib`. No local llama.cpp integration exists.
- **Shutdown**: FastAPI lifespan closes the SQLite global connection.

### Frontend
- **Dev server**: `npm run dev` → Vite on `http://localhost:5173` with proxy `/api` → `http://127.0.0.1:8000`.
- **Build**: `npm run build` → `dist/` directory (static files).
- **Production serving**: No production static server is configured. `npm run preview` serves on port 4173 but is intended for local preview only.
- **API Key**: `import.meta.env.VITE_API_KEY` (browser-observable). No `frontend/.env.example` exists.
- **API Base URL**: `import.meta.env.VITE_API_BASE_URL` defaults to `''` (relies on Vite proxy in dev).

### Database
- **SQLite**: File-based at `recoverai.db` in the working directory. WAL journal mode. 3 migration files (`001_initial.sql`, `002_add_workflow_state.sql`, `003_audit.sql`).
- **Test mode**: Uses in-memory SQLite with shared cache.

### MCP
- **Architecture**: Embedded in the FastAPI process. NOT a separate service/process.
- **Transport**: HTTP via FastAPI route `POST /mcp/execute`.
- **Authentication**: Requires `N8N_API_KEY` (P17).
- **14 registered tools**: 7 READ, 3 ANALYZE, 4 ACT (with policy/verification constraints).

### LLM Gateway
- **Architecture**: Embedded in the FastAPI process.
- **Providers**: Gemini (`gemini-2.5-pro`), Groq (`llama3-70b-8192`), HuggingFace (`Meta-Llama-3-70B-Instruct`).
- **Local model (llama.cpp / Qwen3-8B)**: **NOT IMPLEMENTED**. Zero references to `llama.cpp` or `Qwen` exist anywhere in the codebase. The LLM Gateway exclusively uses external cloud API providers.
- **Configuration**: `GatewayConfig.from_env()` reads `GEMINI_API_KEY`, `GROQ_API_KEY`, `HF_API_KEY` directly from `os.getenv()`.

### n8n
- **Runtime**: Docker container via `n8n/compose.yaml` (image `docker.n8n.io/n8nio/n8n:1.76.3`).
- **Port**: `5678:5678`.
- **Backend connectivity**: `RECOVERAI_API_URL=http://host.docker.internal:8000`.
- **5 workflows**: `customer-notification`, `error-handler`, `human-approval`, `payment-recovery`, `payment-verification`.

### Razorpay
- **Mode**: Test Mode (`razorpay_mode=test`).
- **Webhook endpoint**: `POST /webhooks/razorpay/{merchant_id}`.
- **Authentication**: HMAC-SHA256 signature via `X-Razorpay-Signature`.
- **Tunnel**: No tunneling solution exists in the repository. Local webhook testing requires an external tunnel (e.g., ngrok) which is an **external deployment requirement**, not a repository dependency.

### Configuration
- **Root `.env`**: Exists but is MISSING P17 security variables (`FRONTEND_API_KEY`, `N8N_API_KEY`, `FRONTEND_CORS_ORIGIN`).
- **Root `.env.example`**: Identical to `.env` and also MISSING P17 variables.
- **Frontend `.env`**: Does NOT exist. No `frontend/.env.example` exists.
- **n8n compose.yaml**: MISSING `N8N_API_KEY` environment variable.

### Existing Startup
- `scripts/setup.ps1`: Runs `uv sync` and copies `.env.example` → `.env`.
- `scripts/start.ps1`: Runs `uv run python -m recoverai.main` (P01 bootstrap, NOT the FastAPI server).
- `scripts/test.ps1`: Runs `uv run pytest tests/`.
- `scripts/lint.ps1`: Runs ruff format/check and mypy.
- No unified startup script exists that starts all services.

### Existing Health
- `GET /health` → `{"status": "ok"}` (unauthenticated, minimal).
- No health checks for n8n, LLM availability, or database readiness.

### Existing Deployment
- `deployment/` directory exists but is **empty**.
- No Dockerfile for the backend (by design — native Windows).
- No production deployment scripts.

## 5. Current Runtime Architecture

```
Browser (localhost:5173)
   |
   v [VITE_API_KEY in X-API-Key]
Vite Dev Server (localhost:5173)
   |
   | proxy /api → http://127.0.0.1:8000
   v
FastAPI Backend (localhost:8000)
   |
   +---→ SQLite (recoverai.db, WAL mode)
   |
   +---→ MCP (embedded, /mcp/execute)
   |       |
   |       +---→ PolicyEngine (P07)
   |       +---→ StateMachine (P05)
   |       +---→ RazorpayService (P08)
   |
   +---→ LLM Gateway (embedded)
   |       |
   |       +---→ Gemini API (external HTTPS)
   |       +---→ Groq API (external HTTPS)
   |       +---→ HuggingFace API (external HTTPS)
   |
   +---→ CORSMiddleware (allows localhost:5173)
   |
   +---← Razorpay Webhooks (requires HMAC, external inbound)

n8n (Docker, localhost:5678)
   |
   +---→ POST http://host.docker.internal:8000/mcp/execute
         [N8N_API_KEY in X-API-Key]
```

## 6. Target Deployment Architecture

The target architecture is identical to the current architecture with corrections:

```
Browser (localhost:5173)
   |
   v [VITE_API_KEY in X-API-Key]
Vite Dev Server (localhost:5173) OR Static Server (localhost:4173)
   |
   | proxy /api → http://127.0.0.1:8000
   v
FastAPI/Uvicorn Backend (localhost:8000)
   |
   +---→ SQLite (recoverai.db, WAL mode)
   +---→ MCP (embedded)
   +---→ LLM Gateway (embedded, cloud providers)
   +---→ CORSMiddleware (configured origin)
   +---← Razorpay Webhooks (HMAC only)

n8n (Docker, localhost:5678)
   |
   +---→ POST http://host.docker.internal:8000/mcp/execute
         [N8N_API_KEY via $env.N8N_API_KEY]
```

### llama.cpp / Qwen3-8B Q4_K_M Status

**NOT IMPLEMENTED**. The repository contains zero references to `llama.cpp`, `Qwen`, or local model inference. The LLM Gateway architecture exclusively uses external cloud API providers (Gemini, Groq, HuggingFace). P18 must document this as a gap. If local model inference is desired, it would require:
- Installing llama.cpp on Windows
- Downloading Qwen3-8B Q4_K_M GGUF model
- Adding a new provider adapter to `recoverai/llm_gateway/providers.py`
- Configuring the model path and llama.cpp server port

This is **out of P18 scope** and would be a separate future package.

## 7. Process/Service Inventory

| Process | Type | Host | Port | Native/Docker | Startup Command |
|---|---|---|---|---|---|
| FastAPI Backend | Python ASGI | localhost | 8000 | Native | `uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000` |
| Vite Dev Server | Node.js | localhost | 5173 | Native | `npm run dev` (from `frontend/`) |
| Vite Preview | Node.js | localhost | 4173 | Native | `npm run preview` (from `frontend/`) |
| n8n | Docker | localhost | 5678 | Docker | `docker compose -f n8n/compose.yaml up -d` |
| SQLite | Embedded | N/A | N/A | Native | Initialized by FastAPI backend |
| MCP | Embedded | N/A | N/A | Native | Initialized by FastAPI backend |
| LLM Gateway | Embedded | N/A | N/A | Native | Initialized by FastAPI backend |

## 8. Networking & Ports

| Connection | Source | Target | Port | Protocol | Auth | Direction |
|---|---|---|---|---|---|---|
| Browser → Frontend | Browser | Vite | 5173 | HTTP | None | Outbound |
| Frontend → Backend | Vite proxy | FastAPI | 8000 | HTTP | `X-API-Key: FRONTEND_API_KEY` | localhost |
| n8n → MCP | n8n container | FastAPI | 8000 | HTTP | `X-API-Key: N8N_API_KEY` | `host.docker.internal` |
| Razorpay → Webhook | Razorpay servers | FastAPI | 8000 | HTTPS (via tunnel) | HMAC signature | Inbound (external) |
| Backend → Gemini | FastAPI | googleapis.com | 443 | HTTPS | API Key header | Outbound |
| Backend → Groq | FastAPI | api.groq.com | 443 | HTTPS | Bearer token | Outbound |
| Backend → HuggingFace | FastAPI | api-inference.huggingface.co | 443 | HTTPS | Bearer token | Outbound |

### Exposure Levels
- **localhost-only**: FastAPI (8000), Vite (5173), n8n (5678)
- **Publicly exposed**: None by default. Razorpay webhooks require an external tunnel for testing.
- **Browser-accessible**: Vite dev server (5173)
- **Server-only**: n8n API key, LLM provider keys, Razorpay secrets

## 9. Environment Configuration

### Backend `.env` (Required Variables)

| Variable | Required | Default | Type | Description |
|---|---|---|---|---|
| `ENVIRONMENT` | No | `development` | String | Environment name |
| `LOG_LEVEL` | No | `INFO` | String | Logging level |
| `RAZORPAY_MODE` | No | `test` | String | `test` or `live` |
| `RAZORPAY_KEY_ID` | Yes (for Razorpay) | `None` | String | Razorpay API Key ID |
| `RAZORPAY_KEY_SECRET` | Yes (for Razorpay) | `None` | String | Razorpay API Key Secret |
| `RAZORPAY_WEBHOOK_SECRET` | Yes (for webhooks) | `None` | String | Razorpay Webhook Secret |
| `GEMINI_API_KEY` | Yes (for LLM) | `None` | String | Gemini API Key |
| `GROQ_API_KEY` | Optional | `None` | String | Groq API Key |
| `HF_TOKEN` | Optional | `None` | String | HuggingFace Token |
| `DATABASE_URL` | No | `sqlite:///recoverai.db` | String | Database URL |
| `N8N_BASE_URL` | Optional | `None` | String | n8n Base URL |
| `N8N_API_TOKEN` | Optional | `None` | String | n8n API Token |
| `FRONTEND_API_KEY` | Yes | `test_frontend_key_default` | String | Frontend client credential (browser-observable) |
| `N8N_API_KEY` | Yes | `test_n8n_key_default` | String | n8n orchestrator secret (server-side ONLY) |
| `FRONTEND_CORS_ORIGIN` | No | `http://localhost:5173` | String | Allowed CORS origin |

### Frontend `.env` (Vite Variables)

| Variable | Required | Default | Type | Description |
|---|---|---|---|---|
| `VITE_API_BASE_URL` | No | `''` | String | API base URL (empty = use proxy) |
| `VITE_API_KEY` | Yes | `''` | String | Frontend API key (browser-observable, NOT a secret) |

### n8n Environment (Docker Compose)

| Variable | Required | Default | Type | Description |
|---|---|---|---|---|
| `RECOVERAI_API_URL` | Yes | `http://host.docker.internal:8000` | String | Backend API URL |
| `N8N_API_KEY` | Yes | (none) | String | Server-side secret for MCP access |
| `N8N_HOST` | No | `localhost` | String | n8n host binding |
| `N8N_PORT` | No | `5678` | String | n8n port |
| `WEBHOOK_URL` | No | `http://localhost:5678/` | String | n8n webhook base URL |

### Unsafe Defaults
- `FRONTEND_API_KEY=test_frontend_key_default` — Must be changed for demo/production.
- `N8N_API_KEY=test_n8n_key_default` — Must be changed for demo/production.
- `RAZORPAY_WEBHOOK_SECRET` falls back to `"secret"` in `main.py` if unset — acceptable for local dev but unsafe for deployment.

### Browser-Exposed Values
- `VITE_API_KEY` — intentionally browser-observable; NOT a confidential secret.
- `VITE_API_BASE_URL` — public configuration.

### Server-Only Values
- `N8N_API_KEY`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `HF_TOKEN`.

## 10. Secret Management

- Secrets loaded via `pydantic-settings` from `.env` file or OS environment variables.
- `.env` is in `.gitignore` — will NOT be committed.
- `.env.example` contains only placeholders.
- No secret manager integration (appropriate for local MVP).
- Audit redaction (`AuditEvent.redact_secrets()`) prevents secrets from appearing in audit logs.
- Logging module (`recoverai/logging.py`) uses structured format; `recoverai/main.py` explicitly avoids logging exception details that might contain secrets.

## 11. Startup Dependency Graph

```
1. Validate environment (.env exists, required variables set)
      |
2. Start FastAPI/Uvicorn Backend (port 8000)
      |  - SQLite initialized (migrations run automatically)
      |  - MCP registry created (embedded)
      |  - LLM Gateway initialized (embedded)
      |  - CORS configured
      |  - P17 authentication active
      |
3. Verify backend health: GET http://localhost:8000/health → {"status":"ok"}
      |
4. Start n8n (Docker, port 5678)
      |  - Requires: backend already running (for host.docker.internal:8000)
      |  - Requires: N8N_API_KEY in container environment
      |
5. Verify n8n health: http://localhost:5678 accessible
      |
6. Start Frontend (Vite dev server, port 5173)
      |  - Requires: backend already running (for proxy)
      |  - Requires: VITE_API_KEY in frontend/.env
      |
7. Verify frontend: http://localhost:5173 accessible
      |
8. (Optional) Import/activate n8n workflows
      |
9. End-to-end smoke test
```

### Failure Behavior by Component

| Component | Prerequisite | Failure if unavailable |
|---|---|---|
| Backend | `.env`, Python 3.11+, `uv` | All other services fail |
| SQLite | Backend process | Backend fails to start |
| MCP | Backend process | n8n workflows fail |
| LLM Gateway | Backend process + API keys | AI analysis unavailable; other features work |
| n8n | Docker, Backend running | Orchestration workflows unavailable; UI reads still work |
| Frontend | Node.js, Backend running | No UI; API still accessible |

## 12. Shutdown Procedure

1. **Frontend**: `Ctrl+C` on Vite dev server process (or `npm run dev` process).
2. **n8n**: `docker compose -f n8n/compose.yaml down`.
3. **Backend**: `Ctrl+C` on Uvicorn process. FastAPI lifespan closes SQLite connection.
4. **SQLite**: Automatically handled by backend shutdown. WAL mode ensures crash safety.

### SQLite Safety
- WAL journal mode provides crash recovery.
- `PRAGMA foreign_keys = ON` enforces referential integrity.
- Connections are properly closed in `lifespan` context manager and `transaction()` context manager.

## 13. Health & Readiness

### Existing Health
- `GET /health` → `{"status": "ok"}` — unauthenticated, minimal, safe.

### Proposed Additional Internal Checks (for startup script only, NOT publicly exposed)
- Backend readiness: `curl http://localhost:8000/health`
- n8n readiness: `curl http://localhost:5678` (returns n8n UI)
- Frontend readiness: `curl http://localhost:5173` (returns HTML)

These checks should be in the startup script, NOT new API endpoints.

## 14. Failure & Recovery Matrix

| Failure | Detection | User Impact | Automatic Recovery | Manual Recovery | Data Risk |
|---|---|---|---|---|---|
| Backend crash | Health check fails | All features unavailable | None | Restart Uvicorn | SQLite WAL provides crash safety |
| Frontend crash | Page unreachable | No UI (API still works) | None | Restart Vite |  None |
| n8n crash | Docker health | Orchestration unavailable | Docker `restart: unless-stopped` | `docker compose up -d` | None |
| LLM unavailable | Provider error in logs | AI analysis fails, other features work | Provider fallback chain | Check API keys | None |
| SQLite corrupt | Backend startup failure | All features unavailable | None | Restore from backup | Data loss possible |
| Razorpay unavailable | Webhook 4xx/5xx | Payment recovery actions fail | None | Check Razorpay status | None |
| Webhook rejected | 400 response | Events not ingested | None | Verify HMAC secret | Missed events |
| Invalid environment | Backend fails to start | Nothing works | None | Fix `.env` | None |
| Port collision | Bind error in logs | Affected service unavailable | None | Kill conflicting process | None |
| Frontend unavailable | Page unreachable | No UI | None | Restart Vite | None |
| Expired/incorrect API key | 401/403 responses | Affected operations fail | None | Update keys in `.env` | None |
| Partially started system | Health checks fail | Partial functionality | None | Complete startup sequence | None |
| Model missing (llama.cpp) | N/A (not implemented) | N/A | N/A | N/A | N/A |
| n8n missing N8N_API_KEY | 401 from backend | Workflows fail | None | Add to compose.yaml env | None |

## 15. Windows Runtime Requirements

| Requirement | Version | Purpose | Install |
|---|---|---|---|
| Python | ≥ 3.11 | Backend runtime | python.org / winget |
| uv | Latest | Python package management | `winget install astral-sh.uv` |
| Node.js | ≥ 18 | Frontend build/dev | nodejs.org / winget |
| npm | Bundled with Node | Package management | Bundled |
| Docker Desktop | Latest | n8n sidecar | docker.com |
| Git | Latest | Version control | git-scm.com |

### Windows-Specific Concerns
- **Path separators**: Python `pathlib` handles this correctly throughout the codebase.
- **SQLite path**: `sqlite:///recoverai.db` creates the file in the working directory.
- **PowerShell**: All scripts use PowerShell (`*.ps1`).
- **Process management**: No process manager (pm2, supervisor) exists. Processes run in terminal windows.
- **Port conflicts**: Default ports (8000, 5173, 5678) must be available.
- **Firewall**: Windows Firewall may prompt on first run of each service.

## 16. Frontend Deployment

### Development
```powershell
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Demo/Build
```powershell
cd frontend
npm run build
npm run preview
# → http://localhost:4173
```

### Environment
Create `frontend/.env`:
```ini
VITE_API_KEY=<FRONTEND_API_KEY>
VITE_API_BASE_URL=
```

## 17. Backend Deployment

### Development
```powershell
# From project root
uv sync
uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Demo
```powershell
uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000
```

## 18. MCP Deployment

MCP is embedded inside the FastAPI process. No separate deployment required.

- Exposed at: `POST /mcp/execute`
- Authentication: `X-API-Key: <N8N_API_KEY>`
- 14 tools registered automatically on backend startup.

## 19. LLM Gateway Deployment

LLM Gateway is embedded inside the FastAPI process. No separate deployment required.

- Provider cascade: Gemini → Groq → HuggingFace.
- Requires at least one valid API key (`GEMINI_API_KEY`, `GROQ_API_KEY`, or `HF_TOKEN`).
- If no API keys are configured, AI analysis features will fail with `GatewayError` but other features continue working.

## 20. llama.cpp / Qwen3-8B Q4_K_M Deployment

**STATUS: NOT IMPLEMENTED**

The repository contains zero references to `llama.cpp`, `Qwen`, `GGUF`, or local model inference. The LLM Gateway exclusively uses external cloud API providers.

If local model support is desired in a future package:
1. Install llama.cpp server binary for Windows.
2. Download Qwen3-8B-Q4_K_M.gguf model file.
3. Add a `LlamaCppAdapter` to `recoverai/llm_gateway/providers.py`.
4. Add `LLAMA_CPP_URL` to `GatewayConfig`.
5. Configure startup order (llama.cpp must start before backend).

**This is out of P18 scope.**

## 21. n8n Deployment

### Start
```powershell
docker compose -f n8n/compose.yaml up -d
```

### Access
- UI: `http://localhost:5678`
- Workflows must be imported manually via the n8n UI.

### Required Fix: compose.yaml
Add `N8N_API_KEY` to the environment section:
```yaml
environment:
  - N8N_API_KEY=<N8N_API_KEY>
```

### Required Fix: Workflow Expressions
All workflow JSON files use broken expression `={{ .N8N_API_KEY }}`. Correct syntax is `={{ $env.N8N_API_KEY }}`.

Affected files:
- `workflows/n8n/customer-notification.json`
- `workflows/n8n/human-approval.json`
- `workflows/n8n/payment-recovery.json`
- `workflows/n8n/payment-verification.json`

### Additional Workflow Issues (Documentation Only)
- `payment-recovery.json`: `"connections": {}` is empty — nodes are disconnected.
- `human-approval.json`: Webhook node placement may be structurally incorrect for n8n execution semantics.
- `error-handler.json`: Stub with a single NoOp node.

## 22. Razorpay Test Mode Deployment

- Mode: `RAZORPAY_MODE=test`
- Credentials: Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` from Razorpay Test Dashboard.
- Webhook secret: Set `RAZORPAY_WEBHOOK_SECRET` from Razorpay Webhook configuration.
- **Webhook URL**: Requires a public tunnel (e.g., ngrok) to expose `localhost:8000/webhooks/razorpay/{merchant_id}` to Razorpay servers. No tunnel is included in the repository — this is an external operational requirement.

## 23. SQLite Persistence

- **Path**: `recoverai.db` in the working directory (configurable via `DATABASE_URL`).
- **Journal mode**: WAL (Write-Ahead Logging) for crash safety and better concurrency.
- **Migrations**: 3 SQL files applied automatically on backend startup.
- **Backup**: No automated backup. Manual copy of `recoverai.db` suffices.
- **In `.gitignore`**: `*.db`, `*.db-shm`, `*.db-wal` are all excluded from version control.

## 24. Logging

- Backend: `recoverai/logging.py` — structured format to stdout: `[timestamp] [level] [logger] message`.
- Frontend: Browser console (standard React/Vite).
- n8n: Docker container logs (`docker logs recoverai_n8n`).
- No log aggregation or rotation configured (appropriate for MVP).

## 25. Security Deployment Invariants

P18 deployment MUST preserve:

| Control | Package | Status |
|---|---|---|
| Razorpay webhook HMAC | P04 | IMPLEMENTED — Preserve |
| State machine transitions | P05 | IMPLEMENTED — Preserve |
| Policy engine constraints | P07 | IMPLEMENTED — Preserve |
| Execution boundary | P08 | IMPLEMENTED — Preserve |
| Verification engine | P09 | IMPLEMENTED — Preserve |
| API authentication (`X-API-Key`) | P17 | IMPLEMENTED — Preserve |
| API authorization (role separation) | P17 | IMPLEMENTED — Preserve |
| CORS (restrictive origin) | P17 | IMPLEMENTED — Preserve |
| Secret configuration (Settings) | P17 | IMPLEMENTED — Preserve |
| Frontend credential limitation | P17 | IMPLEMENTED — Preserve |
| Server-side n8n credential | P17 | IMPLEMENTED — Preserve |
| Audit redaction | P14 | IMPLEMENTED — Preserve |
| No arbitrary HTTP/SQL tool | Architecture | IMPLEMENTED — Preserve |
| No credential in LLM context | Architecture | IMPLEMENTED — Preserve |
| Rate limiting | — | **NOT IMPLEMENTED** |
| SSRF protection | — | **NOT IMPLEMENTED** |
| Production TLS | — | **NOT IMPLEMENTED** |
| User authentication | — | **NOT IMPLEMENTED** |
| Database encryption | — | **NOT IMPLEMENTED** |

## 26. Configuration Matrix

| File | Purpose | Creates/Modifies | New/Existing |
|---|---|---|---|
| `.env.example` | Backend environment template | Modify (add P17 vars) | Existing |
| `frontend/.env.example` | Frontend environment template | Create | New |
| `n8n/compose.yaml` | n8n Docker config | Modify (add N8N_API_KEY) | Existing |
| `workflows/n8n/*.json` | n8n workflow definitions | Modify (fix expressions) | Existing |
| `scripts/start-all.ps1` | Unified startup script | Create | New |
| `scripts/stop-all.ps1` | Unified shutdown script | Create | New |
| `scripts/check-health.ps1` | Health verification script | Create | New |
| `deployment/README.md` | Deployment guide | Create | New |

## 27. Deployment Commands

### Backend
| Action | Command |
|---|---|
| Install | `uv sync` |
| Configure | Copy `.env.example` to `.env`, fill values |
| Start (dev) | `uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000 --reload` |
| Start (demo) | `uv run uvicorn recoverai.api.main:app --host 127.0.0.1 --port 8000` |
| Health | `curl http://localhost:8000/health` |
| Stop | `Ctrl+C` |
| Test | `uv run pytest tests/` |

### Frontend
| Action | Command |
|---|---|
| Install | `cd frontend && npm install` |
| Configure | Create `frontend/.env` with `VITE_API_KEY` |
| Start (dev) | `npm run dev` |
| Start (preview) | `npm run build && npm run preview` |
| Health | `curl http://localhost:5173` |
| Stop | `Ctrl+C` |

### n8n
| Action | Command |
|---|---|
| Start | `docker compose -f n8n/compose.yaml up -d` |
| Health | `curl http://localhost:5678` |
| Stop | `docker compose -f n8n/compose.yaml down` |
| Logs | `docker logs recoverai_n8n` |
| Import workflow | Via n8n UI |

## 28. Proposed Files to Create/Modify

### [NEW] `frontend/.env.example`
- **Purpose**: Template for frontend environment variables.
- **Owner**: Frontend deployment.
- **Dependencies**: None.
- **Why needed**: No frontend environment example exists. Developers have no guidance on `VITE_API_KEY`.

### [MODIFY] `.env.example`
- **Purpose**: Add P17 security variables.
- **Owner**: Backend configuration.
- **Dependencies**: None.
- **Why needed**: Current `.env.example` is missing `FRONTEND_API_KEY`, `N8N_API_KEY`, `FRONTEND_CORS_ORIGIN`.

### [MODIFY] `n8n/compose.yaml`
- **Purpose**: Add `N8N_API_KEY` to container environment.
- **Owner**: n8n deployment.
- **Dependencies**: Requires P17 `N8N_API_KEY` to be defined.
- **Why needed**: Without this, `$env.N8N_API_KEY` inside workflows evaluates to empty.

### [MODIFY] `workflows/n8n/*.json` (4 files)
- **Purpose**: Fix broken expression syntax `{{ .N8N_API_KEY }}` → `{{ $env.N8N_API_KEY }}`.
- **Owner**: n8n workflow configuration.
- **Dependencies**: n8n compose.yaml must provide `N8N_API_KEY`.
- **Why needed**: Current expressions are invalid n8n syntax and resolve to undefined.

### [NEW] `scripts/start-all.ps1`
- **Purpose**: Unified startup script that starts all services in correct order.
- **Owner**: Deployment.
- **Dependencies**: uv, npm, Docker.
- **Why needed**: No unified startup exists.

### [NEW] `scripts/stop-all.ps1`
- **Purpose**: Unified shutdown script.
- **Owner**: Deployment.
- **Dependencies**: None.
- **Why needed**: No unified shutdown exists.

### [NEW] `scripts/check-health.ps1`
- **Purpose**: Verify all services are running.
- **Owner**: Deployment verification.
- **Dependencies**: Running services.
- **Why needed**: No health verification script exists.

### [MODIFY] `scripts/start.ps1`
- **Purpose**: Update to start the actual FastAPI server instead of P01 bootstrap.
- **Owner**: Backend deployment.
- **Dependencies**: uv.
- **Why needed**: Current script runs `recoverai.main` (P01 bootstrap) not the FastAPI server.

### [NEW] `deployment/README.md`
- **Purpose**: Complete deployment guide.
- **Owner**: Documentation.
- **Dependencies**: None.
- **Why needed**: `deployment/` directory is empty.

## 29. Implementation Sequence

1. **Environment Configuration**: Update `.env.example` with P17 variables. Create `frontend/.env.example`.
2. **n8n Fix**: Add `N8N_API_KEY` to `n8n/compose.yaml`. Fix workflow expression syntax.
3. **Startup Script**: Update `scripts/start.ps1` to start Uvicorn. Create `scripts/start-all.ps1`, `scripts/stop-all.ps1`, `scripts/check-health.ps1`.
4. **Deployment Documentation**: Create `deployment/README.md`.
5. **P18 Documentation**: Create `docs/checkpoints/package-18.md` and `docs/reports/package-18/implementation_report.md`.
6. **Verification**: Run full test suite, build, lint, format, mypy.

## 30. Verification Strategy

### Regression Gates (must remain green)
- `uv run pytest tests/` → 160 tests pass
- `npm run build` → Frontend builds successfully
- `uv run ruff check .` → No lint errors
- `uv run ruff format --check .` → No format issues
- `uv run mypy recoverai/ tests/` → No type errors

### Deployment Verification
- Backend starts: `uv run uvicorn recoverai.api.main:app --port 8000` → `GET /health` returns `{"status": "ok"}`
- Frontend builds: `npm run build` succeeds
- n8n starts: `docker compose -f n8n/compose.yaml up -d` → `http://localhost:5678` accessible
- CORS rejects unintended origins
- `FRONTEND_API_KEY` works on read endpoints
- `FRONTEND_API_KEY` returns 403 on `/mcp/execute`
- `N8N_API_KEY` works on `/mcp/execute`
- `/health` works without authentication
- Webhook HMAC remains authoritative
- No secrets committed (`git grep` for known test defaults)
- No secrets in logs (manual inspection)

## 31. Definition of Done

P18 is complete when:
- [ ] `.env.example` includes all P17 security variables
- [ ] `frontend/.env.example` exists with `VITE_API_KEY` and `VITE_API_BASE_URL`
- [ ] `n8n/compose.yaml` includes `N8N_API_KEY` environment variable
- [ ] n8n workflow expressions use correct `$env.N8N_API_KEY` syntax
- [ ] `scripts/start.ps1` starts the actual FastAPI server
- [ ] `scripts/start-all.ps1` provides unified startup
- [ ] `scripts/stop-all.ps1` provides unified shutdown
- [ ] `scripts/check-health.ps1` verifies all services
- [ ] `deployment/README.md` documents the complete deployment procedure
- [ ] Native Windows deployment works without Docker (except n8n sidecar)
- [ ] All services have deterministic startup procedures
- [ ] Environment configuration is fully documented
- [ ] Secrets remain protected (`.env` in `.gitignore`)
- [ ] Networking is documented (ports, protocols, directions)
- [ ] P01–P17 remain frozen
- [ ] All 160 regression tests remain green
- [ ] Frontend build remains green
- [ ] Ruff, format, mypy all pass
- [ ] Repository is clean

## 32. Deployment Gaps

### P18-GAP-001: Missing P17 Variables in .env.example
- **Current state**: `.env.example` does not include `FRONTEND_API_KEY`, `N8N_API_KEY`, `FRONTEND_CORS_ORIGIN`.
- **Expected state**: All configurable variables documented in `.env.example`.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\.env.example`
- **Severity**: HIGH — Developers cannot discover P17 configuration requirements.
- **Solution**: Add P17 variables with placeholder values.
- **Affected**: Backend configuration.

### P18-GAP-002: No Frontend .env.example
- **Current state**: No `frontend/.env.example` exists.
- **Expected state**: Frontend environment template with `VITE_API_KEY` and `VITE_API_BASE_URL`.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\frontend\` — no `.env*` files.
- **Severity**: MEDIUM — Frontend developers have no guidance on API key configuration.
- **Solution**: Create `frontend/.env.example`.
- **Affected**: Frontend deployment.

### P18-GAP-003: n8n compose.yaml Missing N8N_API_KEY
- **Current state**: `n8n/compose.yaml` does not include `N8N_API_KEY` in the environment section.
- **Expected state**: `N8N_API_KEY` available inside the n8n container.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\n8n\compose.yaml` — only 6 env vars defined.
- **Severity**: CRITICAL — n8n workflows cannot authenticate with the backend.
- **Solution**: Add `N8N_API_KEY` to compose.yaml environment.
- **Affected**: n8n → MCP communication.

### P18-GAP-004: Broken n8n Workflow Expressions
- **Current state**: All 4 workflow HTTP request nodes use `={{ .N8N_API_KEY }}` which is invalid n8n syntax.
- **Expected state**: `={{ $env.N8N_API_KEY }}` (correct n8n expression syntax).
- **Evidence**: `workflows/n8n/customer-notification.json`, `human-approval.json`, `payment-recovery.json`, `payment-verification.json`.
- **Severity**: CRITICAL — All n8n → backend authenticated requests will fail.
- **Solution**: Fix expression syntax in all 4 workflow files.
- **Affected**: n8n workflow execution.

### P18-GAP-005: scripts/start.ps1 Runs Wrong Entrypoint
- **Current state**: `scripts/start.ps1` runs `uv run python -m recoverai.main` (P01 bootstrap that just logs and exits).
- **Expected state**: Should start `uvicorn recoverai.api.main:app`.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\scripts\start.ps1`
- **Severity**: HIGH — Primary startup script does not start the actual server.
- **Solution**: Update to run Uvicorn.
- **Affected**: Backend startup.

### P18-GAP-006: No Unified Startup/Shutdown Scripts
- **Current state**: No script to start all services in order.
- **Expected state**: `scripts/start-all.ps1` and `scripts/stop-all.ps1`.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\scripts\` — only `lint.ps1`, `setup.ps1`, `start.ps1`, `test.ps1`.
- **Severity**: MEDIUM — Manual multi-terminal startup required.
- **Solution**: Create unified scripts.
- **Affected**: Developer experience, demo deployment.

### P18-GAP-007: Empty deployment/ Directory
- **Current state**: `deployment/` directory is completely empty.
- **Expected state**: Contains deployment documentation.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\deployment\`
- **Severity**: MEDIUM — No deployment guide exists.
- **Solution**: Create `deployment/README.md`.
- **Affected**: Documentation.

### P18-GAP-008: No llama.cpp / Qwen3-8B Integration
- **Current state**: Zero references to `llama.cpp`, `Qwen`, `GGUF`, or local model inference in the entire codebase.
- **Expected state**: Per the deployment architecture specification, local LLM inference via llama.cpp with Qwen3-8B Q4_K_M should be available.
- **Evidence**: `grep -r "llama.cpp" recoverai/` → 0 results. `grep -r "Qwen" recoverai/` → 0 results.
- **Severity**: HIGH (architectural gap) — but **OUT OF P18 SCOPE** (P18 is deployment, not new feature implementation).
- **Solution**: Document as a known gap. If required, create a future package for local LLM integration.
- **Affected**: LLM Gateway, model inference.

### P18-GAP-009: No Health Verification Script
- **Current state**: No script to verify all services are running.
- **Expected state**: `scripts/check-health.ps1` that checks backend, frontend, and n8n health.
- **Evidence**: `c:\Users\Dell\Desktop\RecoverAI\scripts\`
- **Severity**: LOW — Manual health checks work but are tedious.
- **Solution**: Create health check script.
- **Affected**: Deployment verification.

### P18-GAP-010: payment-recovery.json Empty Connections
- **Current state**: `"connections": {}` leaves 3 nodes disconnected.
- **Expected state**: Nodes should be connected sequentially.
- **Evidence**: `workflows/n8n/payment-recovery.json`
- **Severity**: MEDIUM — Workflow will not execute as intended.
- **Solution**: Fix connections in workflow JSON.
- **Affected**: n8n payment recovery orchestration.

### P18-GAP-011: GatewayConfig Duplicates Settings
- **Current state**: `GatewayConfig` in `recoverai/llm_gateway/config.py` reads env vars directly via `os.getenv()`, duplicating what `recoverai/config.py` Settings already handles. Also uses `HF_API_KEY` while Settings uses `HF_TOKEN`.
- **Expected state**: Single source of truth for configuration.
- **Evidence**: `recoverai/llm_gateway/config.py` vs `recoverai/config.py`
- **Severity**: LOW — Functionally works but creates maintenance risk.
- **Solution**: Document inconsistency. Full fix would be P10 scope (frozen).
- **Affected**: LLM Gateway configuration.

## 33. Stop Conditions

**DO NOT EXECUTE IMPLEMENTATION.**

Do not modify source code.
Do not modify workflows.
Do not create deployment scripts.
Do not create Docker files.
Do not start P19.
Do not start P20.
Do not invoke Stitch MCP.

The only deliverable from this task is the P18 forensic implementation plan and associated planning documentation.
