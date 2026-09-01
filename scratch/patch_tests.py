import re

with open('tests/unit/intelligence/test_analyzer.py', 'r') as f:
    text = f.read()

text = text.replace('return [', 'return ("MockLLM", [')
text = text.replace('return candidates', 'return ("MockLLM", candidates)')

with open('tests/unit/intelligence/test_analyzer.py', 'w') as f:
    f.write(text)

with open('tests/unit/llm_gateway/test_engine.py', 'r') as f:
    text2 = f.read()

text2 = text2.replace('candidates = gateway.generate_intervention_candidates', 'provider, candidates = gateway.generate_intervention_candidates')

with open('tests/unit/llm_gateway/test_engine.py', 'w') as f:
    f.write(text2)

