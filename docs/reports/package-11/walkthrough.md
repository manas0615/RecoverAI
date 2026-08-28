# Package 11 Walkthrough

This package introduces the mcp module serving as the translation boundary for LLM agents or MCP clients.

## How it works

1. **Initialization**: A client constructs the MCPContext injecting the database TransactionManager, the RecoveryStateMachine, the PolicyEngine, and the RazorpayExecutionService.
2. **Registration**: create_mcp_registry(ctx) creates a tool registry loaded with 14 endpoints explicitly outlined by the architecture.
3. **Execution**: The client invokes egistry.execute("create_payment_link", {"case_id": "case_1", "action_id": "act_1"}).
4. **Validation**: The registry uses the CreatePaymentLinkInput Pydantic model to assert inputs.
5. **Business Logic**: The handler attempts to generate an InterventionPlan and pass it to the PolicyEngine. If denied, a safe POLICY_DENIAL structure is returned. If approved, execution proceeds to the Razorpay integration.
6. **Error Masking**: If a DB corrupts or an unexpected failure arises, it is masked as an INTERNAL_ERROR rather than exposing Python internal structures.

## Testing
We comprehensively covered test cases for:
- Valid data retrieval (get_recovery_case).
- Missing or malformed inputs generating INVALID_INPUT.
- Policy denials properly translating to POLICY_DENIAL.
- Idempotency on duplicated create_payment_link attempts.
- Unsupported methods mapping accurately to UNSUPPORTED_TOOL.
