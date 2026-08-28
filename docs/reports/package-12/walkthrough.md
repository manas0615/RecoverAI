# Package 12 Walkthrough

## Connecting n8n to RecoverAI
This implementation configures n8n as an isolated orchestrator running in a local Docker sidecar, designed to communicate directly with the local RecoverAI backend without requiring Razorpay Live credentials or public tunneling inside the n8n environment itself.

1. **Docker Sidecar Boot**: 
   Running docker compose -f n8n/compose.yaml up -d will deploy the orchestrator.
2. **Networking**: 
   The orchestrator uses host.docker.internal:8000 to locate the native Windows API.
3. **Trigger**: 
   When a recovery process spans multiple hours (e.g., waiting for a payment link to be paid), n8n executes the payment-recovery.json workflow.
4. **Step 1 - Act**: 
   n8n fires an HTTP request to the RecoverAI MCP API for create_payment_link. RecoverAI handles validation, policy checking, and returns an execution receipt.
5. **Step 2 - Wait**: 
   n8n's visual engine enters a suspend state (Wait node) without holding any database locks.
6. **Step 3 - Verify**: 
   n8n fires the ssess_recovery_case command back to RecoverAI to query whether the state transition resolved to PAID. 
   The result dictates the next orchestration step, delegating all domain logic entirely to the Python backend.
