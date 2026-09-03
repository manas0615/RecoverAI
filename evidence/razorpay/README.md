# Real Razorpay Evidence

RecoverAI executes financial operations against the live Razorpay Test Mode API. This directory indexes the real executions (A001–A005) that drove the engineering of the system.

## Provider Evidence Index

| Case | Amount | Outcome | Engineering Significance |
|:---|:---|:---|:---|
| [A001](A001.md) | ₹100 | Verified Recovery | Baseline successful end-to-end recovery loop. |
| [A002](A002.md) | ₹450 | Verified Recovery | Repeat baseline across a different value. |
| [A003](A003.md) | ₹750 | **Failed Recovery** | Real failed recovery that exposed the critical closed-loop correlation defect. |
| [A004](A004.md) | ₹1,000 | Verified Recovery | Successful recovery proving the A003 loop fix was effective. |
| [A005](A005.md) | ₹50,000 | Policy Gap Found | Historical high-value wiring gap discovery. |

*Note: Cases A003 and A005 document historical, pre-fix system states. They are preserved precisely because they demonstrate real failures caught via provider execution.*
