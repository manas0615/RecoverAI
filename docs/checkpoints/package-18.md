# Package 18: Deployment Implementation

**Status:** IMPLEMENTED AND VERIFIED.

## Summary
Package 18 implements the concrete deployment architecture for the RecoverAI MVP on a native Windows environment (with an n8n Docker sidecar). It fixes critical configuration gaps, repairs n8n workflow expressions, and provides unified PowerShell orchestration scripts for deterministic startup, shutdown, and health verification.

## Architecture
- **Backend/Frontend**: Native Windows (Python/uv, Node.js/npm)
- **Database**: Native SQLite (`recoverai.db`)
- **n8n Orchestration**: Docker sidecar (`docker compose`)
- **LLM / MCP**: Embedded natively within the FastAPI backend

## Files Created/Modified
- `[NEW] frontend/.env.example`
- `[NEW] scripts/start-all.ps1`
- `[NEW] scripts/stop-all.ps1`
- `[NEW] scripts/check-health.ps1`
- `[NEW] deployment/README.md`
- `[MODIFY] .env.example`
- `[MODIFY] n8n/compose.yaml` (Added `N8N_API_KEY`)
- `[MODIFY] workflows/n8n/*.json` (Repaired `{{ $env.N8N_API_KEY }}` expression syntax and empty connections in `payment-recovery.json`)
- `[MODIFY] scripts/start.ps1` (Switched to Uvicorn FastAPI server)

## Security Invariants Maintained
- `FRONTEND_API_KEY` remains a browser-observable credential for read access.
- `N8N_API_KEY` remains a server-side orchestrator secret.
- Webhook HMAC logic remains authoritative.
- No local LLM (llama.cpp/Qwen3) was implemented (documented as out of scope).

## Next Package Boundary
P19 (Integration & Failure Testing) will focus on end-to-end failure injection and component resiliency testing across this deployed architecture.
