# RecoverAI Frontend Console

The `frontend` directory contains the React SPA (Single Page Application) that serves as the operator console for RecoverAI. It provides visibility into the recovery pipeline, AI reasoning, and execution state.

## Architecture

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS / custom components
- **Routing**: React Router

## Key Capabilities

1. **Dashboard Overview**: Aggregated analytics on recovery throughput, systemic degradation status, and policy intervention metrics.
2. **Case Management**: Real-time queue of `payment.failed` cases requiring analysis.
3. **Recovery Journey Timeline**: A visual audit trail for a specific case, displaying every `Event` from initial ingestion to final verification.
4. **Analysis & Execution**: Interface to trigger the `RevenueIntelligenceAnalyzer` and review the LLM's `InterventionPlan` before the `PolicyEngine` authorizes execution.
5. **Human Approval Queue**: High-value cases (`> ₹40k`) routed by the policy engine to `ESCALATE` appear here for manual override.

## API Integration

The frontend communicates with the FastAPI backend over REST. 
- Base URL is determined by the `.env` configuration (default: `http://localhost:8000/api`).
- API requests require passing the `x-api-key` header to penetrate the prototype backend security perimeter.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

*Note: Ensure the backend is running and the database is seeded for local development.*
