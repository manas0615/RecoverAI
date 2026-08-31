import os
import glob

files = glob.glob('frontend/src/**/*.tsx', recursive=True) + glob.glob('frontend/src/**/*.ts', recursive=True)
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '../hooks/useCases' in content:
        content = content.replace('../hooks/useCases', '../hooks/useApi')
    if '../../hooks/useCases' in content:
        content = content.replace('../../hooks/useCases', '../../hooks/useApi')
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed imports")
