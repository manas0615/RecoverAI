# AI / LLM FORENSIC AUDIT — FINAL REPORT

## 1. Executive Finding
Gemini and Groq were not producing recommendations due to a combination of missing environment credentials (GEMINI_API_KEY absent from .env), a decommissioned model configuration for Groq (llama3-70b-8192), and a strict 10-second HTTP timeout in providers.py causing valid structural generations to abort early. However, even if they succeeded, the application suffered from a hardcoded provenance bug: ecoverai/api/main.py always used the isk.model_name ("deterministic_baseline") for the API response and the database audit actor ID, completely ignoring the LLM plan.selection_model_version, causing the frontend to always display "Deterministic Fallback".

## 2. End-to-End Call Chain
Analyze Case
→ API (POST /recovery-cases/{id}/analyze)
→ Intelligence (nalyzer.analyze())
→ Gateway (LLMGateway.generate_intervention_candidates())
→ Provider (GeminiAdapter.generate_json())
→ Parser (InterventionPlanResponseModel)
→ Recommendation (nalyzer._build_plan_from_candidates)
→ Audit (AuditActor(id=risk.model_name))  *(Root Cause Bug!)*
→ UI (caseData.provenance)

## 3. Configuration Findings
.env → Settings → GatewayConfig → Provider
- GEMINI_API_KEY: missing from .env (configured=false originally).
- GROQ_API_KEY: missing from .env (configured=false originally).
- After injection, GatewayConfig successfully passed these values to GeminiAdapter and GroqAdapter.

## 4. Gemini Findings
- configured? Yes (after injection)
- provider initialized? Yes
- endpoint: https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent
- model: gemini-3.6-flash
- request accepted? Yes, but large JSON generations often exceeded the 10-second timeout, resulting in TimeoutError: The read operation timed out.
- exact safe error class: TimeoutError
- response parsing result: Successful once timeout increased to 30s.
- fallback trigger: Previously timed out, causing ProviderError, leading to deterministic fallback.

## 5. Groq Findings
- configured? Yes (after injection)
- provider initialized? Yes
- endpoint: https://api.groq.com/openai/v1/chat/completions
- model: llama3-70b-8192 (Original)
- request accepted? No.
- HTTP status: 400
- exact safe error class: model_decommissioned
- response parsing result: Failed due to 400 Bad Request.
- fallback trigger: Decommissioned model caused ProviderError. (Updated model to llama-3.1-70b-versatile).

## 6. Fallback Findings
Deterministic fallback executes exclusively when LLMGateway throws GatewayError or ValueError (meaning all providers failed). It uses simple heuristics based on customer failure counts and returns deterministic_1.0 as the plan version.

## 7. Response Schema Findings
Provider responses successfully mapped into the InterventionPlanResponseModel contract when the models were given sufficient time (30s timeout) and proper model versions.

## 8. Provenance Findings
Before fix:
- UI: Checked caseData.provenance
- Audit: Hardcoded to isk.model_name (deterministic_baseline)
- API: Returned model_version: risk.model_version
- Provider: Handled LLM call, but result was silently discarded for provenance.

After fix:
- UI, Audit, API, and Provider all trace plan.selection_model_version, which evaluates to Gemini, Groq, or deterministic_1.0.

## 9. Root Cause
- **CREDENTIAL/PROVIDER ACCESS PROBLEM**: Missing keys in .env.
- **MODEL/ENDPOINT PROBLEM**: Groq model llama3-70b-8192 was decommissioned, and Gemini/Groq timeouts were too aggressive (10s) for structured JSON generation.
- **APPLICATION BUG**: ecoverai/api/main.py explicitly hardcoded the LLM audit trace and API response provenance to the deterministic risk model, permanently suppressing any successful AI provenance from reaching the UI.

## 10. Fix Applied
- ecoverai/llm_gateway/providers.py: Increased 	imeout to 30s and properly bubbled underlying exception names.
- ecoverai/llm_gateway/config.py: Updated groq_model to llama-3.1-70b-versatile.
- ecoverai/llm_gateway/engine.py & ecoverai/intelligence/analyzer.py: Modified generate_intervention_candidates to return a 	uple[str, list[InterventionCandidate]], capturing the successful provider's name (e.g. Gemini).
- ecoverai/api/main.py: Replaced model_version: risk.model_version with model_version: plan.selection_model_version, and ctor=AuditActor(id=risk.model_name) with ctor=AuditActor(id=plan.selection_model_version).
- 	ests/unit/intelligence/test_analyzer.py & 	ests/unit/llm_gateway/test_engine.py: Updated tests to match the new tuple signature.

## 11. Direct Provider Sanity Tests
Gemini: Succeeded!
Groq: Succeeded! (after fixing model to llama-3.1-70b-versatile)

## 12. End-to-End case_LIVE Test
Provider: Gemini
Recommendation: CREATE_PAYMENT_LINK
Provenance: Gemini
Policy: APPROVE
Audit: ctor.id = Gemini

## 13. Fallback Test
Removing .env keys successfully forced the application to gracefully skip all LLM providers and execute _deterministic_intervention_plan(), returning deterministic_1.0 and displaying "Deterministic Fallback" in the UI.

## 14. Browser Verification
Actual result: Analyzed case_LIVE. The button switched to "Analyzing...", and gracefully returned a recommendation natively verified by Gemini. The "Gemini" badge rendered cleanly next to the recommendation.

## 15. Tests
uv run python -m pytest tests/ -q
Result: 184 passed, 4 warnings in 6.10s

## 16. Build
cd frontend; npm run build
Result: ✓ built in 981ms

## 17. Files Changed
- recoverai/llm_gateway/providers.py
- recoverai/llm_gateway/config.py
- recoverai/llm_gateway/engine.py
- recoverai/intelligence/analyzer.py
- recoverai/api/main.py
- tests/unit/intelligence/test_analyzer.py
- tests/unit/llm_gateway/test_engine.py

## 18. Remaining Blockers
None.
