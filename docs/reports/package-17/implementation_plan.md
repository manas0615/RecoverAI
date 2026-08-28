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
- Implement secure CORS policies.

## 12. Authentication Requirements
- Introduce API key validation via standard FastAPI header dependencies (`X-API-Key`).
- Define `FRONTEND_API_KEY` and `N8N_API_KEY` in application settings.

## 13. Authorization Requirements
- **Frontend Endpoints:** `GET /recovery-cases`, `GET /recovery-cases/{id}`, `GET /recovery-cases/{id}/timeline` require `X-API-Key: <FRONTEND_API_KEY>`.
- **MCP Execution:** `POST /mcp/execute` requires `X-API-Key: <N8N_API_KEY>`.
- **Webhooks:** `POST /webhooks/razorpay/*` remain exclusively authorized via HMAC signature verification.
- **Healthcheck:** `GET /health` remains unauthenticated.

## 14. API Hardening
- Add `CORSMiddleware` to `main.py`, restricting origins based on a new `frontend_cors_origin` configuration setting.

## 15. Webhook Hardening
- **NOT APPLICABLE** — Signature verification and duplicate handling were robustly implemented in P04. No changes needed.

## 16. MCP Hardening
- Lock down `POST /mcp/execute` exclusively to the `N8N_API_KEY` role.

## 17. n8n Boundary Hardening
- Update existing n8n workflows (`workflows/n8n/*.json`) to inject `X-API-Key: {{$env.N8N_API_KEY}}` into `httpRequest` nodes targeting the MCP endpoint.

## 18. LLM Boundary Hardening
- Ensure `ConcreteLLMGateway` initializes using API keys sourced from `Settings` rather than potentially empty kwargs.

## 19. Secrets & Configuration Hardening
- Refactor `AppContainer` in `recoverai/api/main.py` to source `RazorpayConfig` (key_id, key_secret), `WebhookVerifier` (secret), and `GatewayConfig` from the unified `recoverai.config.Settings`.

## 20. Data/Persistence Hardening
- **NOT APPLICABLE** — No SQL injection risks detected in the ORM/Query layer. SQLite operates strictly on the local filesystem.

## 21. Logging/Audit Hardening
- **NOT APPLICABLE** — Redaction logic (`redact_secrets`) within `recoverai/domain/audit.py` is thoroughly implemented.

## 22. Error/Information Disclosure Hardening
- Ensure FastAPI's default handlers do not leak backend stack traces to unauthenticated clients. Standard 401/403 responses will be enforced for missing/invalid keys.

## 23. Dependency/Supply-Chain Hardening
- **NOT APPLICABLE** — P17 restricts scope to application hardening. Dependency versions remain frozen.

## 24. Security Test Strategy
- **API Tests:** Verify 401 Unauthorized for requests missing keys.
- **Authz Tests:** Verify `FRONTEND_API_KEY` is rejected at `/mcp/execute`.
- **Authz Tests:** Verify `N8N_API_KEY` is accepted at `/mcp/execute`.
- **Config Tests:** Verify `AppContainer` initializes correctly using environment configurations instead of mocks.

## 25. Implementation Sequence
1. **Secrets & Configuration:** Update `recoverai/config.py` to include `frontend_api_key`, `n8n_api_key`, and `frontend_cors_origin`. Update `AppContainer` to use these settings.
2. **Authentication Middleware:** Create `recoverai/api/security.py` to define API key dependencies.
3. **Route Hardening:** Apply dependencies to `main.py` routes and add `CORSMiddleware`.
4. **Test Adjustments:** Update `tests/unit/api/test_api.py` to pass appropriate headers during testing.
5. **Frontend Integration:** Update `frontend/src/api/client.ts` to include the API key header.
6. **n8n Integration:** Update `workflows/n8n/*.json` files to include the API key header.

## 26. Files/Modules Expected to Change
- `recoverai/config.py`
- `recoverai/api/main.py`
- `recoverai/api/security.py` (New)
- `tests/unit/api/test_api.py`
- `frontend/src/api/client.ts`
- `workflows/n8n/*.json`

## 27. Files/Modules Explicitly Frozen
- `recoverai/domain/*`
- `recoverai/policy/*`
- `recoverai/persistence/*`
- `recoverai/integrations/*`
- `frontend/src/components/*`
- `frontend/src/pages/*`
- `frontend/src/index.css`

## 28. Documentation Changes
- `docs/checkpoints/package-17.md`
- `docs/reports/package-17/implementation_report.md`
- Update `docs/security.md` Verification Status to mark Authentication, Rate Limits, and CORS as VERIFIED.

## 29. Verification Gates
- `uv run pytest tests/`
- `npm run build`
- `uv run ruff check .`
- `uv run mypy recoverai/ tests/`

## 30. Definition of Done
- No endpoints (except `/health` and webhooks) are accessible without an API key.
- Hardcoded secrets are permanently removed from `AppContainer`.
- Frontend correctly passes API keys.
- All tests pass locally.

## 31. Stop Conditions
- **DO NOT EXECUTE IMPLEMENTATION.** Only generate this plan document.
- Do not modify source code or workflows.
- Do not start P18.
