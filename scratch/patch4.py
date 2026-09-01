import re

with open('tests/unit/intelligence/test_analyzer.py', 'r') as f:
    text = f.read()

# Fix generate_intervention_candidates signatures
text = re.sub(
    r'\) -> list\[InterventionCandidate\]:',
    r') -> tuple[str, list[InterventionCandidate]]:',
    text
)

# Fix MockLLMGateway return
text = re.sub(
    r'return \[\s*InterventionCandidate\(',
    r'return ("MockLLM", [\n            InterventionCandidate(',
    text
)
text = re.sub(
    r'reason="Mock generated",\s*\)\s*\]',
    r'reason="Mock generated",\n        )])',
    text
)

# Fix IneligibleCandidateGateway return
text = text.replace('return [ineligible_candidate]', 'return ("MockLLM", [ineligible_candidate])')


with open('tests/unit/intelligence/test_analyzer.py', 'w') as f:
    f.write(text)

