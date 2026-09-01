import re

with open('frontend/src/pages/CaseDetail.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the useEffect block and move it up.
effect_block = '''  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isAnalyzing && id) {
      interval = setInterval(() => {
        refetch();
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isAnalyzing, id, refetch]);'''

content = content.replace(effect_block, '')

# And insert it above the if (loading)
insertion_point = content.find('  if (loading || !data) {')
content = content[:insertion_point] + effect_block + '\n\n' + content[insertion_point:]

with open('frontend/src/pages/CaseDetail.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
