# Package 15: Walkthrough

## How to execute the API Layer

The API can be run dynamically using uvicorn:

\\\ash
uv run uvicorn recoverai.api.main:app --host 0.0.0.0 --port 8000
\\\

## Component Boundaries

1. **Frontend to API**:
   - Frontend calls GET /recovery-cases.
   - ecoverai.api.main extracts the SQLite connection using the TransactionManager.
   - RecoveryCaseRepository is instantiated and delegates data access.
   - Returned entities are safely mapped to a public JSON representation (via case_to_dict).

2. **n8n Orchestration to API**:
   - n8n node sends POST /mcp/execute with body {"tool": "analyze_root_cause", "args": {...}}.
   - API delegates parsing to MCPToolRegistry.execute(tool, args).
   - Schema validation runs via MCP input schema definition (AnalyzeRootCauseInput).
   - Result is serialized to JSON and passed back synchronously to the n8n webhook caller.

3. **Webhook to API**:
   - Razorpay issues POST /webhooks/razorpay/M123.
   - FastAPI extracts raw body buffer, X-Razorpay-Signature, and X-Razorpay-Event-Id.
   - Transmits fields to WebhookIngestionService.process_webhook.
   - Catches internal EventIngestionErrors (like DuplicateEvent or Signature Mismatch) and maps to safe 400 Bad Request HTTP errors without leaking sensitive stack traces.
