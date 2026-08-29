# RecoverAI Deployment Guide

This guide describes how to deploy the RecoverAI MVP on a native Windows environment. The architecture is Docker-free (except for the n8n sidecar orchestration).

## 1. Prerequisites

Ensure the following are installed:
- **Python ≥ 3.11** (via `python.org` or `winget`)
- **uv** (via `winget install astral-sh.uv`)
- **Node.js ≥ 18** (via `nodejs.org` or `winget`)
- **Docker Desktop** (required ONLY for n8n)
- **Git**

## 2. Repository Setup

1. Clone the repository and navigate into the root directory.
2. Run the setup script to install dependencies:
   ```powershell
   .\scripts\setup.ps1
   ```
   This will run `uv sync` and create a placeholder `.env` file from `.env.example`.
3. Install frontend dependencies:
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

## 3. Environment Configuration

### Server Configuration (`.env`)
Open `.env` in the root directory. At minimum, configure:
- **`FRONTEND_API_KEY`**: A browser-observable client credential used by the frontend to authenticate read-only operations. (Default is `test_frontend_key_default`).
- **`N8N_API_KEY`**: A server-side secret used by n8n to execute MCP tools. **Keep this secret.**
- **`FRONTEND_CORS_ORIGIN`**: The allowed CORS origin for the frontend (e.g., `http://localhost:5173`).
- **`GEMINI_API_KEY`** (or Groq/HF equivalent): Your API key for the LLM Gateway.
- **`RAZORPAY_KEY_ID`**, **`RAZORPAY_KEY_SECRET`**, **`RAZORPAY_WEBHOOK_SECRET`**: Your Razorpay Test Mode credentials.

### Frontend Configuration (`frontend/.env`)
Create `frontend/.env` (you can copy from `frontend/.env.example`):
```ini
VITE_API_KEY=test_frontend_key_default
VITE_API_BASE_URL=
```
Make sure `VITE_API_KEY` matches the `FRONTEND_API_KEY` in your root `.env`.

> **SECURITY WARNING:** `VITE_API_KEY` is bundled into the frontend client and is observable in the browser. Do NOT use it for `N8N_API_KEY` or any backend-only secret.

## 4. Starting the Full System

We provide a unified startup script that sequentially launches the Backend, n8n, and Frontend:

```powershell
.\scripts\start-all.ps1
```

This script will:
1. Validate prerequisites.
2. Start the FastAPI backend in a new console window (port 8000).
3. Wait for backend health (`/health`).
4. Start n8n via Docker Compose (port 5678).
5. Start the Vite Frontend in a new console window (port 5173).

## 5. Checking Health

You can verify that all services are running properly with:
```powershell
.\scripts\check-health.ps1
```
Expected output should show `[OK]` for Backend, n8n, and Frontend.

## 6. Stopping the System

To gracefully stop all services started by the unified script:
```powershell
.\scripts\stop-all.ps1
```
This will shut down the n8n Docker container and terminate the Node and Python processes running on ports 5173 and 8000. Alternatively, you can simply close the popup console windows for the backend and frontend.

## 7. Razorpay Test Mode Setup & Webhook Tunnel

The application integrates with Razorpay **Test Mode** (`RAZORPAY_MODE=test`).
For local development, Razorpay's servers must be able to reach your backend webhook endpoint:
`POST /webhooks/razorpay/{merchant_id}`

You must use an external tunnel like ngrok:
```powershell
ngrok http 8000
```
Update your Razorpay Dashboard Webhook settings with the generated ngrok URL and your `RAZORPAY_WEBHOOK_SECRET`.

## 8. Common Failures

- **Port Collisions**: If ports 8000, 5678, or 5173 are already in use, the services will fail to start. Use `Get-NetTCPConnection` to identify and kill the conflicting process.
- **Missing API Keys**: If `N8N_API_KEY` is missing in `n8n/compose.yaml` (should be handled automatically), workflows will return HTTP 401.
- **Workflow Execution Failure**: Workflows require manual import/activation inside the n8n UI at `http://localhost:5678`.

## 9. Logs & Persistence

- **Backend Logs**: Available in the popup console window (stdout in structured format).
- **n8n Logs**: Run `docker logs recoverai_n8n`.
- **Database**: SQLite data is saved persistently to `recoverai.db` in the project root. It runs in WAL mode for safety.
