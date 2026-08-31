import re

# 1. Patch API
with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    api_content = f.read()

api_content = api_content.replace(
    'if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED, ActionStatus.EXECUTING]:',
    'if latest_action.status in [ActionStatus.PROPOSED, ActionStatus.AUTHORIZED]:'
)

with open('recoverai/api/main.py', 'w', encoding='utf-8') as f:
    f.write(api_content)


# 2. Patch Frontend
with open('frontend/src/pages/ExecutionQueue.tsx', 'r', encoding='utf-8') as f:
    ui_content = f.read()

old_button = """          <button 
            onClick={handleAbort}
            disabled={aborting || isCompleted || !isAuthorized}
            className="w-full px-4 py-2 text-xs font-medium bg-[var(--color-surface)] border border-red-500/50 text-red-400 rounded hover:bg-red-500/10 transition-colors focus:outline-none disabled:opacity-50"
          >
            {aborting ? 'Aborting...' : 'Abort Execution'}
          </button>"""

new_button = """          <button 
            onClick={handleAbort}
            disabled={aborting || isExecuting || isCompleted || !['PROPOSED', 'AUTHORIZED'].includes(c.action_status || '')}
            className={`w-full px-4 py-2 text-xs font-medium rounded transition-colors focus:outline-none disabled:opacity-50 ${
              isExecuting || isCompleted 
                ? 'bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-muted)]' 
                : 'bg-[var(--color-surface)] border border-red-500/50 text-red-400 hover:bg-red-500/10'
            }`}
          >
            {aborting ? 'Aborting...' : isExecuting || isCompleted ? 'Execution in progress — cannot cancel' : 'Abort Execution'}
          </button>"""

ui_content = ui_content.replace(old_button, new_button)

with open('frontend/src/pages/ExecutionQueue.tsx', 'w', encoding='utf-8') as f:
    f.write(ui_content)
