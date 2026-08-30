# RecoverAI

**Razorpay AI Buildathon — Track 03: AI Revenue Recovery**

RecoverAI is an evidence-first, bounded AI revenue-recovery system. It detects revenue at risk, applies intelligent analysis to determine the optimal recovery strategy, enforces deterministic policy to ensure financial safety, and executes bounded recovery workflows via Razorpay.

## Architecture

RecoverAI implements a strict Trust Boundary separating AI reasoning from financial execution.

### System Architecture Detailed
```mermaid
graph TD
    UI[Frontend Dashboard] --> API[Backend API]
    API --> IN[Ingestion Engine]
    IN --> CM[Case Manager]
    API --> RI[Revenue Intelligence]
    RI --> PE[Policy Engine]
    PE --> RA[Recovery Action Service]
    RA --> RZ[Razorpay Adapter]
    RZ --> VE[Verification Engine]
    VE --> API
```

### AI / Policy Trust Boundary
```mermaid
graph TD
    subgraph AI Suggests
        A[Analyze Case] --> B[Gemini Gateway]
        B --> C["Recommended Action & Reasoning"]
    end
    subgraph Policy Decides
        C --> D{Policy Rules}
        D --> |APPROVE| E[Allow Execution]
        D --> |SUPPRESS| F[Block Execution]
        D --> |ESCALATE| G[Require Human Approval]
    end
```

### Financial Execution Path
```mermaid
graph TD
    A[Policy Approved] --> B[RecoveryActionService]
    B --> C{Action Type}
    C --> |PAYMENT_LINK| D[Razorpay Payment Link API]
    C --> |RETRY| E[Razorpay Payment Retry API]
```

### Verification Path
```mermaid
graph TD
    A[Razorpay Webhook] --> B[Ingestion: payment_link.paid]
    B --> C[VerificationEngine]
    C --> D[Match with RecoveryAction]
    D --> E[Transition Case to VERIFIED_SUCCESS]
```

### UNKNOWN / Failure Safety Flow
```mermaid
graph TD
    A[RecoveryActionService] --> B[Razorpay API]
    B --> |Timeout / 500| C[EXECUTION_UNKNOWN]
    C --> D[System halts retries on this case]
    D --> E[Reconciliation Process takes over]
    B --> |400 Bad Request| F[FAILURE]
    F --> G[Log Failure, no blind retry]
```

### User Journey
```mermaid
graph LR
    A[Dashboard] --> B[Cases List]
    B --> C[Select Case]
    C --> D[Review Evidence]
    D --> E[Analyze Case]
    E --> F["View AI & Policy"]
    F --> G[Execution Result]
    G --> H[Audit Timeline]
```

### Key Principles
1. **AI Suggests, Policy Decides:** LLM outputs (Gemini) are strictly recommendations. They cannot directly execute financial mutations.
2. **Evidence-First:** Every AI decision is grounded in verifiable case context and payment events. 
3. **Single Financial Authority:** The `RecoveryActionService` is the sole pathway to Razorpay mutations.

## Features
- **Intelligent Case Analysis:** Analyzes payment failure reasons, systemic degradations, and high-value sensitivities.
- **Truthful Analytics:** Computes *Revenue at Risk* and *Verified Recovered* based on authoritative API verification, with strict currency partitioning (INR vs USD).
- **Audit Timeline:** Human-readable audit trails for every state transition, with technical payloads accessible for debugging.
- **n8n Orchestration:** Workflow integration for complex case handling.

## Setup Instructions (Windows)

Prerequisites: Python 3.11+, Node.js (for frontend), and `uv` package manager.

1. **Bootstrap Environment:**
   ```powershell
   Copy-Item .env.example .env
   Copy-Item frontend\.env.example frontend\.env
   ```
2. **Configure API Keys:**
   Open `.env` and set `GEMINI_API_KEY` and Razorpay credentials (if testing live execution).
3. **Start Infrastructure:**
   ```powershell
   .\scripts\start-all.ps1
   ```
4. **Health Check:**
   ```powershell
   .\scripts\check-health.ps1
   ```

## Demo & Verification

**Deterministic Demo Data:**
Seed a curated set of 7 cases proving safety invariants and pipeline states (SUCCESS, FAILURE, UNKNOWN, DENIAL, ESCALATION, DUPLICATE, LIVE DETECTED):
```powershell
uv run scripts/seed_demo_data.py
```

**Evaluation:**
Run the P25 synthetic batch evaluation:
```powershell
uv run python scratch/run_evaluation.py
```

## Safety Guarantees
- **No Fabricated Data:** AI does not invent case context or recommendations prior to explicit "Analyze Case" interactions.
- **UNKNOWN Safety:** Provider uncertainties (e.g. timeouts) result in `UNKNOWN` state, preventing blind retry loops.
- **No Client-Side Execution:** The frontend cannot mutate financial state directly.


## Evaluation & Robustness (P25)
We evaluated RecoverAI on a reproducible 1,500-scenario synthetic benchmark against no intervention and a transparent simple-rule baseline. RecoverAI did not maximize gross recovery: at the baseline configuration it recovered ₹3.16M versus ₹3.36M for the simple rule. Instead, it reduced failed interventions from 558 to 506 and escalated 121 chronic-failure cases. A predeclared sensitivity sweep showed that this recovery-versus-intervention tradeoff remained directionally stable across reasonable parameter changes. These are synthetic evaluation results, not claims of production recovery performance.

## Limitations
- Currency exchange calculation is not implemented; metrics are strictly partitioned by currency.
- Real execution relies on valid Razorpay Test Mode credentials and webhook configurations.

---
*Built for the Razorpay AI Buildathon.*
