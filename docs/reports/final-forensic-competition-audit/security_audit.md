# 7. Security Audit

**Status:** Critical Vulnerabilities (P0 Leakage).

## 1. Secret Leakage (P0)
Active, production-grade secrets are currently stored in unencrypted `.env` files and committed artifacts:
- **Google Gemini API Key**
- **Groq API Key**
- **Razorpay Key ID & Key Secret**
- **Razorpay Webhook Secret**

*Even if `.env` is `.gitignore`d, the scratch scripts and markdown reports (e.g. `p24_full_external_success_verification.md`) contain these plaintext credentials.*

## 2. Dangerous Scratch Scripts
The `scratch/` folder contains scripts that bypass all architectural safety:
- `setup_webhook.py`: Registers live ngrok webhooks directly via HTTP.
- `pay.py`: Uses headless Playwright to autonomously submit live payment links.
- `execute_test_mode.py`: Executes Razorpay actions outside the FastAPI container constraints.
- Code manipulation scripts (`fix_main.py`, `patch_seed.py`) dynamically rewrite source files and database records in place.

## 3. Tenant Authorization (P1)
The system lacks multi-tenant isolation. The API key `X-API-Key` is a static frontend key. `GET /recovery-cases` fetches all cases in the database without filtering by a legally verified `merchant_id`. The README's claim of a "multi-merchant" design is not enforced at the read layer.

**Verdict:** The leaked keys and dangerous scripts must be immediately purged/rotated. The single-tenant reality must be accurately documented.
