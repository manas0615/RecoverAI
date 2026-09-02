from recoverai.persistence.connection import TransactionManager
from recoverai.persistence.repositories.action import RecoveryActionRepository
from recoverai.domain.identifiers import RecoveryActionId
import sqlite3

conn = sqlite3.connect("recoverai.db")
c = conn.cursor()
c.execute("SELECT workflow_execution_reference, external_reference FROM recovery_actions WHERE action_id='act_92b05657512b'")
print(c.fetchone())
