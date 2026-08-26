# RecoverAI

RecoverAI is a revenue-recovery system for the Razorpay AI Buildathon, designed to detect revenue at risk, determine appropriate interventions, and execute bounded recovery workflows.

## Development Status
Current Stage: **Package 01 — Repository & Foundation**
The project currently establishes the core Python engineering foundation (configuration, logging, error handling, testing, and CI). No business logic has been implemented yet.

## Prerequisites
- Windows OS (PowerShell)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer and resolver)

## Local Setup

1. **Bootstrap the environment:**
   Run the setup script to install dependencies and create the `.env` file.
   ```powershell
   .\scripts\setup.ps1
   ```

2. **Environment Configuration:**
   Review `.env` and fill in any placeholder values if you are actively working on an integration package. For foundation work, the defaults will suffice.

## Developer Commands

- **Run Tests:**
  ```powershell
  .\scripts\test.ps1
  ```

- **Run Lint & Type Checks:**
  ```powershell
  .\scripts\lint.ps1
  ```

- **Start Foundation Application:**
  ```powershell
  .\scripts\start.ps1
  ```
