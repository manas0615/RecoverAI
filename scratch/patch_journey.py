import re

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to detect POLICY_DECISION_CREATED and its outcome.
# The user wants:
# APPROVE -> Ready for Execution
# ESCALATE -> Human Approval — CURRENT
# DENY/SUPPRESS -> stop there.

# Let's replace getStageIndexForEvent to handle ANALYSIS_STARTED.
# And we need to adjust the UI nodes loop to inject 'Ready for Execution'.

replacement = '''    const getStageIndexForEvent = (eventType: string) => {
      if (['CASE_CREATED', 'WEBHOOK_RECEIVED', 'ANALYSIS_STARTED'].includes(eventType)) return 0;
      if (['LLM_RECOMMENDATION_CREATED'].includes(eventType)) return 1;
      if (['POLICY_DECISION_CREATED'].includes(eventType)) return 2;
      if (['ACTION_AUTHORIZED', 'CASE_ESCALATED'].includes(eventType)) return 3;
      if (['ACTION_EXECUTING', 'RAZORPAY_REQUEST_COMPLETED'].includes(eventType)) return 4;
      if (['VERIFICATION_STARTED', 'VERIFICATION_COMPLETED', 'RECOVERY_CONFIRMED'].includes(eventType)) return 5;
      return 0;
    };'''
content = re.sub(r'    const getStageIndexForEvent = \(eventType: string\) => \{.*?;', replacement, content, flags=re.DOTALL)

with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
