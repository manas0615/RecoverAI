# Package 12: n8n Workflow Orchestration Implementation Report

## Overview
Package 12 establishes n8n as the isolated orchestration layer for time-bound sequences, scheduled follow-ups, and wait semantics. As specified in the architecture, n8n relies completely on the RecoverAI MCP/API boundary and does not embed any business truth, domain models, or standalone financial rules.

## Core Implementations
- **Docker Compose Setup (
8n/compose.yaml)**: Provides an isolated, native-Windows-compatible Docker configuration targeting n8n v1.20.0. Utilizes host.docker.internal networking to allow the containerized orchestrator safely authenticated reach to the native Windows Python backend without exposing the database to the internet.
- **Workflow Artifacts (workflows/n8n/)**: We have defined the skeleton structure for the 5 mandated workflows:
  - payment-recovery.json: Executes the primary action, waits, and triggers state verification via the MCP interface.
  - payment-verification.json
  - customer-notification.json
  - human-approval.json
  - error-handler.json

## Constraint Validations
- **No Direct Mutation**: Workflows use the generic MCP tool interface endpoints (create_payment_link, ssess_recovery_case). The workflows possess NO capacity to alter a case state without the Python application verifying policy and constraints.
- **Restartability & Secrets**: 
8n_data volumes provide execution persistence. The workflows reference RECOVERAI_API_URL environment variables instead of hardcoding host/credential mappings.
- **Separation of Concerns**: We did NOT Dockerize the native RecoverAI Python backend, honoring P01–P11 constraints.
