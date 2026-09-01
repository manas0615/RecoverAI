import re

with open('frontend/src/pages/CaseDetail.tsx', 'r') as f:
    content = f.read()

# Add useEffect to imports if missing
if 'useEffect' not in content:
    content = content.replace('import { useState }', 'import { useState, useEffect }')

# Add the useEffect polling block
polling_block = '''
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isAnalyzing && id) {
      interval = setInterval(() => {
        refetch();
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAnalyzing, id, refetch]);

  const handleAnalyze = async () => {'''

content = content.replace('  const handleAnalyze = async () => {', polling_block)

with open('frontend/src/pages/CaseDetail.tsx', 'w') as f:
    f.write(content)
