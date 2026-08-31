import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

content = content.replace('rec_rate = (total_verified_cases / total_eligible * 100) if total_eligible > 0 else 0', 'rec_rate = (total_verified_cases / total_eligible * 100) if total_eligible > 0 else None')
content = content.replace('verif_rate = (total_verifications_matched / total_verifications * 100) if total_verifications > 0 else 0', 'verif_rate = (total_verifications_matched / total_verifications * 100) if total_verifications > 0 else None')
content = content.replace('"recovery_rate": round(rec_rate, 1),', '"recovery_rate": round(rec_rate, 1) if rec_rate is not None else None,')
content = content.replace('"verification_rate": round(verif_rate, 1),', '"verification_rate": round(verif_rate, 1) if verif_rate is not None else None,')

with open('recoverai/api/main.py', 'w') as f:
    f.write(content)
