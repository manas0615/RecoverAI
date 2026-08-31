import re

with open('recoverai/api/main.py', 'r') as f:
    content = f.read()

new_endpoint = '''
@app.get("/audit", dependencies=[Depends(require_frontend_key)])
async def get_audit_events():
    with container.tm.transaction() as conn:
        from recoverai.persistence.repositories.audit import AuditRepository
        audit_repo = AuditRepository(conn)
        events = audit_repo.get_all(limit=1000)
        return {"events": [e.to_dict() for e in events]}
'''

if '@app.get("/audit"' not in content:
    content += new_endpoint
    with open('recoverai/api/main.py', 'w') as f:
        f.write(content)
