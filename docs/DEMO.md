# RecoverAI Demo Runbook

This runbook provides instructions for demonstrating RecoverAI locally.

## Prerequisites

1. **Python 3.11+** (managed via `uv`)
2. **Node.js 20+**
3. **Razorpay Test Mode Credentials**
4. **Gemini API Key**

```bash
# Clone and configure
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Populate the `.env` file with:
```env
RAZORPAY_MODE=test
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY
RAZORPAY_KEY_SECRET=YOUR_SECRET
RAZORPAY_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

## Running the Services

**1. Start the Backend API**
```powershell
uv run uvicorn recoverai.api.main:app --reload --port 8000
```

**2. Start the Frontend Console**
```powershell
cd frontend
npm install
npm run dev
```

**3. Seed the Database**
In a new terminal:
```powershell
uv run python scripts/reset_demo_db.py
uv run python scripts/seed_demo_data.py
```

## Demonstration Steps

1. **Navigate to Console:** Open `http://localhost:5173/` in your browser.
2. **View Cases:** Click on "Recovery Cases" to view the seeded failed payment scenarios.
3. **Trigger Ingestion:** Send a mock `payment.failed` webhook via Postman or `curl` to `http://localhost:8000/api/webhooks/razorpay`. *(Ensure the HMAC signature matches).*
4. **Analyze Case:** Open a case detail view and click **Analyze Case**. The system will query Gemini (or gracefully fallback if the API free tier rate-limits you).
5. **Observe Policy Gating:** Notice the AI's `InterventionPlan` is evaluated by the `PolicyEngine`.
6. **Execute:** If the action is `AUTHORIZED`, click **Execute**. This triggers the backend to call the live Razorpay Test Mode API.
7. **Verify Link:** Razorpay returns an external reference (e.g., `plink_xxx`).
8. **Simulate Customer Payment:** Simulate a `payment_link.paid` webhook to the backend containing the exact amount and the `plink_xxx` reference.
9. **Verify Recovery:** Observe the case transition to `VERIFIED_SUCCESS` and gracefully close.

## Running Automated End-to-End Tests
To verify the entire loop automatically without the UI:

```powershell
uv run pytest tests/e2e/test_real_testmode.py -s -v
```

> **WARNING:** Never use production Razorpay credentials. The system is designed to mutate financial state. Always enforce `RAZORPAY_MODE=test`.
