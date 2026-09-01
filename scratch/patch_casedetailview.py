import re

with open('frontend/src/pages/CaseDetailView.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Recommendation area: replace the isAnalyzing loader with a simple button state.
# We also change the 'unanalyzed' condition to ONLY look at the backend state.
# Previously it was: (caseData.recommendation === 'N/A' || !caseData.recommendation) && !caseData.policy_decision && !timeline.some(...)
# Now it should be: (caseData.recommendation === 'N/A' || !caseData.recommendation) && !caseData.policy_decision

content = re.sub(
    r'\{\s*isAnalyzing \? \(\s*<div className="space-y-4 my-8">.*?</div>\s*\)\s*:\s*analyzeError \? \(',
    '{ analyzeError ? (',
    content,
    flags=re.DOTALL
)

content = content.replace(
    "} && !timeline.some(e => ['LLM_RECOMMENDATION_CREATED', 'POLICY_DECISION_CREATED', 'ANALYSIS_STARTED'].includes(e.event_type)) ?",
    "} ?"
)

# In the 'Analyze Case' button, change the text to 'Analyzing...' when isAnalyzing is true.
# Instead of replacing precisely, I'll search for the unanalyzed block button.
content = re.sub(
    r'<button\s+onClick=\{onAnalyze\}\s+disabled=\{isAnalyzing\}\s+className="([^"]+)"\s*>\s*Analyze Case\s*</button>',
    r'<button \n                  onClick={onAnalyze}\n                  disabled={isAnalyzing}\n                  className="\1"\n                >\n                  {isAnalyzing ? "Analyzing..." : "Analyze Case"}\n                </button>',
    content
)

# 2. Policy Checks area: remove the isAnalyzing branch
# It has this structure:
#               {isAnalyzing ? (
#                 <span className="text-[10px] ...">
#                   CHECKING
#                 </span>
#               ) : !caseData.policy_decision ? (
content = re.sub(
    r'\{\s*isAnalyzing \? \(\s*<span[^>]*>\s*CHECKING\s*</span>\s*\)\s*:\s*!caseData\.policy_decision \? \(',
    '{ !caseData.policy_decision ? (',
    content,
    flags=re.DOTALL
)

# Also the Policy Checks reasons loading spinners:
#               {isAnalyzing ? (
#                 <>
#                   <div className="flex items-center gap-3">
#                     <span className="w-4 h-4 rounded-full border-2 border-[var(--color-border)] border-t-[var(--color-primary)] animate-spin shrink-0"></span>
#                     <span className="text-sm text-[var(--color-text-secondary)]">Amount within limit</span>
#                   </div>
# ...
#                 </>
#               ) : !caseData.policy_decision ? (
content = re.sub(
    r'\{\s*isAnalyzing \? \(\s*<>\s*<div.*?</>\s*\)\s*:\s*!caseData\.policy_decision \? \(',
    '{ !caseData.policy_decision ? (',
    content,
    flags=re.DOTALL
)

with open('frontend/src/pages/CaseDetailView.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

