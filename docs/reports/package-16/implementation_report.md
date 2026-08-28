# Package 16: Frontend / Stitch UI

## Overview
Implemented the PRODUCT UI layer using React, TypeScript, and Vite. The frontend architecture follows a "Dark-First" enterprise aesthetic designed via Stitch.

## Features
- **Dashboard Overview**: Displays KPIs (Amount at risk, active cases) and a list of recovery cases fetched from `/api/recovery-cases`.
- **Case Detail View**: A Tri-Fold Intelligence Grid showing AI Intelligence, Policy Decision, and Execution Hub.
- **Audit Timeline**: Displays immutable audit events fetched from `/api/recovery-cases/{id}/timeline`.

## Stitch MCP Integration
- Created a new project "RecoverAI Dashboard" using the Stitch MCP.
- Generated `Dashboard` and `Case Detail` screens.
- Extracted and implemented the following design principles from the Stitch response:
  - Deep Navy (#0F172A) and Dark Slate (#1E293B) theme.
  - Primary Blue (#007AFF) for action states.
  - Use of `Inter` for prose and `JetBrains Mono` for tabular/financial data.
  - "Tri-Fold Intelligence Grid" layout for Case Details.

## Financial Safety
- No business logic or state is evaluated on the client.
- Statuses and rules are fetched deterministically from the P15 backend.
- Executing an action correctly triggers the execution endpoints instead of mutating local state.
