# Package 17 — Security Hardening Implementation Plan

## 1. Executive Summary
Package 17 introduces security hardening to the existing RecoverAI MVP architecture. A forensic review of the repository reveals that while structural security policies (e.g., webhook signatures, policy engine constraints) are correctly implemented, the primary backend API boundaries lack transport-level authentication, and several mock credentials remain hardcoded in the application container. P17 will introduce API key-based authentication, configure secure CORS policies, and eliminate hardcoded mock credentials, ensuring that external UI clients and orchestration tools (n8n) are securely isolated.

## 2. Package Scope
- **API Boundary Hardening:** Introduce FastAPI dependency-based authentication and CORS middleware.
- **Secrets & Configuration Hardening:** Remove hardcoded credentials from the Application Container and strictly enforce loading via `recoverai.config.Settings`.
- **MCP Access Control:** Implement authorization boundaries to isolate `READ_ONLY` operations (Frontend) from `ORCHESTRATOR` operations (n8n via MCP).

## 3. Frozen Constraints
- **P01–P16 Functionality:** Frozen. No business logic or domain models will be altered.
- **Frontend Design:** The "Warm Premium" UI design is frozen.
- **Database Architecture:** Frozen (SQLite).
- **No Scope Creep:** Do not start P18, P19, or P20.

## 4. Repository Reality Assessment
- **Frontend:** Exists as a React SPA communicating with backend `/api/*` endpoints without authentication.
- **Backend API:** Exists in `recoverai/api/main.py`. Does not enforce authentication or authorization (except for Razorpay webhook signatures).
- **Application Container:** `AppContainer` currently hardcodes `"mock"` for Razorpay credentials and `"secret"` for Webhook validation.
- **MCP:** Fully exposed at `POST /mcp/execute` without authentication, though underlying actions (like `CREATE_PAYMENT_LINK`) are correctly guarded by the `PolicyEngine`.
- **Audit Logs:** Secrets are correctly redacted via `AuditEvent.redact_secrets()`.

## 5. Implemented vs Aspirational Capability Matrix
| Concept | Status | Note |
|---|---|---|
| Razorpay Webhooks | **IMPLEMENTED** | Full signature verification and idempotency exist. |
| Audit Redaction | **IMPLEMENTED** | `redact_secrets` logic is active. |
| AI/ML Predictive Models | **NOT PRESENT** | The LLM Gateway uses standard provider APIs for generative reasoning; no native predictive ML exists. |
| Browser-side Financial Execution | **NOT PRESENT** | Intentional design (human approval handled externally via n8n). |
| Database Encryption | **NOT PRESENT** | Standard local SQLite handles persistence directly. |

## 6. Current Security Architecture
- Razorpay webhook verification operates correctly against raw payloads.
- `PolicyEngine` successfully enforces deterministic rules before allowing MCP actions.
- Hardcoded mock credentials in `main.py` represent a local MVP development state, which is unacceptable for deployment.

## 7. Security Attack Surface
- `Frontend -> Backend API`: Unauthenticated. Risks unauthorized data exposure (`GET /recovery-cases`).
- `MCP HTTP Boundary`: Unauthenticated. Exposes system internals and orchestration paths (`POST /mcp/execute`).
- `Configuration/Environment`: Hardcoded strings in `AppContainer` bypass secure environment configuration.

## 8. Threat Model
- **Unauthorized Data Access:** Unauthenticated requests to `GET /recovery-cases`.
- **Unauthorized Orchestration:** Unauthenticated requests triggering workflow actions via `POST /mcp/execute`.
- **Credential Leakage:** Hardcoded test values in `main.py` transitioning into a live environment.

## 9. Findings / Vulnerability Inventory
1. **Unauthenticated API Access:** `GET` endpoints are entirely open.
2. **Unauthenticated MCP Access:** `POST /mcp/execute` is entirely open.
3. **Hardcoded Secrets:** `AppContainer` relies on `"mock"` and `"secret"` instead of `get_settings()`.
4. **Missing CORS:** `main.py` lacks `CORSMiddleware`.

## 10. Risk Classification
- **High:** Hardcoded credentials bypassing configuration.
- **High:** Unauthenticated MCP execution.
- **Medium:** Unauthenticated read-only data access.

## 11. P17 Security Objectives
- Migrate all credentials to `recoverai.config.Settings`.
- Implement `X-API-Key` authentication for the backend API.
- Differentiate authorization levels: `FRONTEND_API_KEY` (read-only UI access) and `N8N_API_KEY` (orchestration access).
  - **IMPORTANT SECURITY LIMITATION**: `FRONTEND_API_KEY` is a lightweight client credential embedded in the browser, not a confidential secret. It prevents completely unauthenticated scraping but does NOT strongly authenticate the human user.
  - `N8N_API_KEY` is a true server-side secret kept strictly out of the browser.
- Implement secure CORS policies.

## 12. Authentication Requirements
- Introduce API key validation via standard FastAPI header dependencies (`X-API-Key`).
- Define `FRONTEND_API_KEY` and `N8N_API_KEY` in application settings.

## 13. Authorization Requirements
- **Authentication**: "Does this request possess a valid credential?"
- **Authorization**: "Is this credential permitted to invoke this endpoint?"
- **Frontend Endpoints:** `GET /recovery-cases`, `GET /recovery-cases/{id}`, `GET /recovery-cases/{id}/timeline` require `X-API-Key: <FRONTEND_API_KEY>`.
- **MCP Execution:** `POST /mcp/execute` strictly requires `X-API-Key: <N8N_API_KEY>`. The frontend credential MUST NOT be authorized to execute MCP tools.
- **Webhooks:** `POST /webhooks/razorpay/*` remain exclusively authorized via Razorpay HMAC signature verification. Do NOT add API key requirements here.
- **Healthcheck:** `GET /health` remains unauthenticated.

## 14. API Hardening (CORS and Health)
- **CORS Middleware:** Add `CORSMiddleware` to `main.py`, restricting origins based on a new `frontend_cors_origin` configuration setting. Ensure NO wildcard origins are used. CORS controls browser-origin access and is NOT a substitute for n8n/server-to-server authentication.
- **Health Endpoint:** `GET /health` will remain unauthenticated as a minimal readiness/availability endpoint. It must only return `{"status": "ok"}` and must NOT expose secrets, provider credentials, database contents, internal topology, dependencies, or sensitive diagnostics, ensuring compatibility with standard orchestration (e.g., Docker/healthchecks) without risking data leaks.

## 15. Webhook Hardening
- **NOT APPLICABLE** — Signature verification and duplicate handling were robustly implemented in P04. No changes needed.
- **SECURITY INVARIANT**: Webhook authentication remains provider-signature based via HMAC. API keys MUST NOT bypass or replace this Razorpay HMAC verification.

## 16. MCP Hardening
- Lock down `POST /mcp/execute` exclusively to the `N8N_API_KEY` role.

## 17. n8n Boundary Hardening
- Update existing n8n workflows (`workflows/n8n/*.json`) to inject `X-API-Key: {{$env.N8N_API_KEY}}` into `httpRequest` nodes targeting the MCP endpoint.

## 18. LLM Boundary Hardening
- Ensure `ConcreteLLMGateway` initializes using API keys sourced from `Settings` rather than potentially empty kwargs.

## 19. Secrets & Configuration Hardening
- Refactor `AppContainer` in `recoverai/api/main.py` to source `RazorpayConfig` (key_id, key_secret), `WebhookVerifier` (secret), and `GatewayConfig` from the unified `recoverai.config.Settings`.
- **SECURITY CORRECTION**: Runtime credentials must come from Settings/environment configuration to ensure that local placeholder credentials (`"mock"`, `"secret"`) are not silently substituted in production environments.

## 20. Security Error Contract
Define the expected safe behavior for the API layer:
- **Missing API key**: Returns `401 Unauthorized`.
- **Invalid API key**: Returns `401 Unauthorized`.
- **Insufficient role (e.g. Frontend Key on MCP route)**: Returns `403 Forbidden`.
- **Internal Exception**: Standard 500 response. Must NOT leak stack traces, database contents, API keys, filesystem paths, SQL queries, provider credentials, or raw exception internals.

## 21. Data/Persistence Hardening
- **NOT APPLICABLE** — No SQL injection risks detected in the ORM/Query layer. SQLite operates strictly on the local filesystem.

## 22. Logging/Audit Hardening
- **NOT APPLICABLE** — Redaction logic (`redact_secrets`) within `recoverai/domain/audit.py` is thoroughly implemented.

## 23. Error/Information Disclosure Hardening
- Ensure FastAPI's default handlers do not leak backend stack traces to unauthenticated clients. Standard 401/403 responses will be enforced for missing/invalid keys.

## 24. Dependency/Supply-Chain Hardening
- **NOT APPLICABLE** — P17 restricts scope to application hardening. Dependency versions remain frozen.

## 25. Security Test Strategy
- **Public Health:**
  - `GET /health` -> succeeds without API key.
  - `GET /health` -> does not expose sensitive information.
- **Read API:**
  - no key -> `401 Unauthorized`.
  - invalid key -> `401 Unauthorized`.
  - valid `FRONTEND_API_KEY` -> succeeds.
- **MCP API:**
  - no key -> `401 Unauthorized`.
  - invalid key -> `401 Unauthorized`.
  - `FRONTEND_API_KEY` -> `403 Forbidden`.
  - valid `N8N_API_KEY` -> succeeds.
- **Webhook:**
  - valid Razorpay signature -> existing behavior preserved.
  - invalid signature -> rejected.
  - API key alone MUST NOT bypass webhook signature verification.
- **Configuration:**
  - Credentials are loaded from `Settings`/environment -> no placeholder runtime credentials silently substituted.
- **Regression:**
  - All existing P01–P16 tests remain green.

## 26. Implementation Sequence
1. **Secrets & Configuration:** Update `recoverai/config.py` to include `frontend_api_key`, `n8n_api_key`, and `frontend_cors_origin`. Update `AppContainer` to use these settings.
2. **Authentication Middleware:** Create `recoverai/api/security.py` to define API key dependencies (`FRONTEND_API_KEY`, `N8N_API_KEY`).
3. **Route Hardening:** Apply dependencies to `main.py` routes and add `CORSMiddleware`. Ensure `/health` remains unauthenticated and webhook routes use only HMAC.
4. **Test Adjustments:** Update `tests/unit/api/test_api.py` to pass appropriate headers during testing and cover the new authz rules.
5. **Frontend Integration:** Update `frontend/src/api/client.ts` to include the API key header (`import.meta.env.VITE_API_KEY`). Note that Vite exposes this to the browser.
6. **n8n Integration:** Update `workflows/n8n/*.json` files to include the API key header (`={{ $env.N8N_API_KEY }}`). Note that this must securely reference the n8n environment, not hardcode the key.

## 27. Files/Modules Expected to Change
- `recoverai/config.py`
- `recoverai/api/main.py`
- `recoverai/api/security.py` (New)
- `tests/unit/api/test_api.py`
- `frontend/src/api/client.ts`
- `workflows/n8n/*.json`

## 28. Files/Modules Explicitly Frozen
- `recoverai/domain/*`
- `recoverai/policy/*`
- `recoverai/persistence/*`
- `recoverai/integrations/*`
- `frontend/src/components/*`
- `frontend/src/pages/*`
- `frontend/src/index.css`

## 29. Documentation Changes
- `docs/checkpoints/package-17.md`
- `docs/reports/package-17/implementation_report.md`
- Update `docs/security.md` Verification Status to mark Authentication, Authorization, and CORS as VERIFIED.
- **RATE LIMITING**: NOT IMPLEMENTED / OUT OF P17 SCOPE. Do not claim verification.

## 30. Verification Gates
- `uv run pytest tests/`
- `npm run build`
- `uv run ruff check .`
- `uv run mypy recoverai/ tests/`

## 31. Definition of Done
- Protected API endpoints require appropriate credentials.
- Read-only and orchestrator credentials are cleanly separated.
- Frontend credential cannot invoke MCP.
- n8n credential is not exposed to the browser.
- Financial actions remain protected by P07/P05/P08.
- Webhook HMAC verification remains authoritative (no API key required/permitted to bypass).
- Runtime credentials come from configuration (Settings).
- No real secrets are committed.
- CORS is restrictive where applicable.
- Safe errors do not leak internals (proper 401/403/500).
- Security tests pass.
- P01–P16 regression remains green.
- Frontend build remains green.
- Repository remains clean.

## 32. Stop Conditions
- **DO NOT EXECUTE IMPLEMENTATION.** Only generate this plan document.
- Do not modify source code or workflows.
- Do not start P18.
