# RecoverAI - End-to-End Razorpay Test Mode Demo

This guide provides instructions to run a complete, end-to-end revenue recovery demonstration using the **Razorpay Test Mode** integration locally.

## Prerequisites
Ensure the .env file contains the correct Razorpay credentials and the mode is set to test:
`env
RAZORPAY_MODE=test
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=
`

## Running the Automated End-to-End Test

The full pipeline—webhook ingestion, intelligent analysis, policy evaluation, external execution (creating a payment link in Razorpay), and asynchronous verification (simulating customer payment)—can be executed automatically.

1. Ensure your virtual environment is active.
2. Run the E2E pytest suite:

`ash
pytest tests/e2e/test_real_testmode.py -s -v
`

This test:
1. Emulates Razorpay sending a payment.failed webhook signed with HMAC.
2. Asserts the case appears in the system queue.
3. Requests AI intervention analysis.
4. Uses MCP /mcp/execute to simulate n8n applying the create_payment_link tool, which generates a real Razorpay test payment link.
5. Simulates a customer paying the link by forging a signed payment_link.paid webhook.
6. Verifies the system successfully marks the recovery as VERIFIED_SUCCESS.

## Running a Manual Demo

To visually verify the system works through the UI:

1. Start the backend:
   `ash
   uv run uvicorn recoverai.api.main:app --reload --port 8000
   `
2. Start the frontend:
   `ash
   cd frontend
   npm run dev
   `
3. Open http://localhost:5173/.
4. Trigger a simulated webhook using a cURL command or Postman matching the HMAC logic in 	est_real_testmode.py.
5. Observe the new case in **Recovery Cases**.
6. Open the Case Detail, click **Analyze Case**.
7. The system will provide an AI recommendation (or Fallback if quota exhausted).
8. The policy engine will auto-approve it.
9. Execution creates a real plink_xxx via Razorpay Test mode.
10. Trigger the second payment_link.paid webhook.
11. Observe the case close as **VERIFIED_SUCCESS**.

> **Note**: Test mode credentials are provided. Ensure you **never** use real production credentials for demo purposes.
