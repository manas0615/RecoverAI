# Package 10: LLM Gateway Walkthrough

## 1. Scenario: Successful Gemini Reasoning
- **Trigger:** P06 invokes synthesize_cause.
- **Gateway Action:** Engine injects the prompt and JSON schema into GeminiAdapter.
- **Response:** Gemini returns structured JSON.
- **Result:** Pydantic validates the JSON and converts it to CauseAssessment.

## 2. Scenario: Gemini Times Out -> Groq Fallback
- **Trigger:** P06 invokes generate_intervention_candidates.
- **Gateway Action:** GeminiAdapter encounters an HTTP timeout or Rate Limit.
- **Fallback:** The gateway swallows the failure and routes the identical prompt/schema to GroqAdapter.
- **Response:** Groq successfully returns the response.
- **Result:** P06 continues uninterrupted using Groq's output.

## 3. Scenario: All Providers Fail
- **Trigger:** Gemini, Groq, and Hugging Face all fail or return invalid/hallucinated JSON.
- **Gateway Action:** Exhausts the fallback chain and raises GatewayError.
- **Result:** P06 catches the exception and securely falls back to its deterministic rule-based assessments. No AI failure compromises the system.
