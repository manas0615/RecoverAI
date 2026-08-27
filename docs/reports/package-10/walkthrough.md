# Package 10: LLM Gateway Walkthrough

## 1. Scenario: Structured Output Validation
- **Trigger:** P06 invokes synthesize_cause.
- **Gateway Action:** Engine injects prompt and schema into GeminiAdapter.
- **Response:** Gemini returns JSON adhering to the explicit schema.
- **Result:** Pydantic safely parses and instantiates CauseAssessment.

## 2. Scenario: JSON Mode Fallback (Groq)
- **Trigger:** Gemini times out or hits rate limits.
- **Fallback:** Engine routes to GroqAdapter using llama3-70b-8192 in JSON Object Mode.
- **Response:** Groq returns JSON (without native schema enforcement).
- **Result:** Application-level Pydantic successfully parses the JSON, validating required fields, ensuring safety before reaching P06.

## 3. Scenario: Auth/Configuration Error
- **Trigger:** Missing API key or Invalid API Key resulting in a 401.
- **Result:** Adapter raises a ConfigurationError. The Engine immediately bubbles this exception rather than cycling through other providers, stopping cost bleeding.
