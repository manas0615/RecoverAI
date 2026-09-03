# Razorpay Provider Evidence

This directory contains technical incident/evidence reports of real Razorpay Test Mode execution.

The most important takeaway from this evidence is the workflow it represents:
**REAL PROVIDER → FAILURE → OBSERVED DEFECT → FIX → REGRESSION → CORRECTED DESIGN**

## Evidence Index
- **A001**: Successful real Razorpay Test Mode recovery.
- **A002**: Successful real Razorpay Test Mode recovery.
- **A003**: Intentionally failed recovery revealing the recovery-loop defect (Historical / Pre-Fix).
- **A004**: Successful recovery after the A003 loop-fix path was implemented.
- **A005**: High-value recovery policy case (Historical / Pre-Fix), proving the threshold wiring gap which was subsequently patched.
