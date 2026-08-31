import subprocess, sys

# Check if RecoveryCase has `.id`, `.provenance`, `.rules_matched`, and action.strategy_type
result = subprocess.run(
    [sys.executable, '-c', '''
from recoverai.domain.case import RecoveryCase
print("has id attr:", hasattr(RecoveryCase, "id") or any("id" == f.name for f in __import__("dataclasses").fields(RecoveryCase) if hasattr(RecoveryCase, "__dataclass_fields__")))
import dataclasses
fields = [f.name for f in dataclasses.fields(RecoveryCase)]
print("case fields:", fields)
from recoverai.domain.action import RecoveryAction
afields = [f.name for f in dataclasses.fields(RecoveryAction)]
print("action fields:", afields)
'''],
    capture_output=True, text=True, cwd='c:/Users/Dell/Desktop/RecoverAI'
)
print(result.stdout)
print(result.stderr)
