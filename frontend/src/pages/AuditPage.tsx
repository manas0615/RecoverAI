import { useState, useMemo } from 'react';
import { useAuditEvents } from '../hooks/useApi';
import { RefreshCw, Filter, Download, ArrowRight } from 'lucide-react';

export function AuditPage() {
  const { data, loading, refetch } = useAuditEvents();
  const events = data?.events || [];
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState('');

  const filteredEvents = useMemo(() => {
    if (!searchQuery) return events;
    const lowerQuery = searchQuery.toLowerCase();
    return events.filter((e: any) => 
      e.audit_event_id.toLowerCase().includes(lowerQuery) || 
      (e.case_id && e.case_id.toLowerCase().includes(lowerQuery))
    );
  }, [events, searchQuery]);

  useMemo(() => {
    if (!selectedEventId && filteredEvents.length > 0) {
      setSelectedEventId(filteredEvents[0].audit_event_id);
    }
  }, [filteredEvents, selectedEventId]);

  const selectedEvent = useMemo(() => {
    return events.find((e: any) => e.audit_event_id === selectedEventId) || null;
  }, [events, selectedEventId]);

  const stats = useMemo(() => {
    const caseIds = new Set(events.filter((e:any) => e.case_id).map((e:any) => e.case_id));
    return {
      total: events.length,
      cases: caseIds.size,
      approvalEvents: events.filter((e:any) => e.event_type === 'ACTION_AUTHORIZED' || e.event_type === 'POLICY_DECISION_CREATED').length,
      verificationEvents: events.filter((e:any) => e.event_type.startsWith('VERIFICATION_') || e.event_type.startsWith('RECOVERY_')).length,
    };
  }, [events]);

  const formatEventName = (type: string) => {
    const mapping: Record<string, string> = {
      'CASE_CREATED': 'Case created',
      'LLM_RECOMMENDATION_CREATED': 'AI recommendation generated',
      'POLICY_DECISION_CREATED': 'Policy decision created',
      'ACTION_AUTHORIZED': 'Human approval recorded',
      'ACTION_EXECUTING': 'Execution queued',
      'RAZORPAY_REQUEST_COMPLETED': 'Provider response received',
      'VERIFICATION_COMPLETED': 'Recovery verified',
      'VERIFICATION_STARTED': 'Verification started',
      'CASE_ESCALATED': 'Escalation recorded',
      'RECOVERY_CONFIRMED': 'Recovery confirmed',
      'WEBHOOK_RECEIVED': 'Evidence collected'
    };
    return mapping[type] || type.replace(/_/g, ' ').toLowerCase();
  };

  const getComponent = (actorType: string, eventType: string) => {
    if (eventType === 'ACTION_EXECUTING' || eventType === 'RAZORPAY_REQUEST_COMPLETED') return 'RecoveryActionService';
    if (eventType === 'POLICY_DECISION_CREATED') return 'PolicyEngine';
    if (eventType === 'LLM_RECOMMENDATION_CREATED') return 'Gemini';
    if (eventType.startsWith('VERIFICATION_') || eventType.startsWith('RECOVERY_')) return 'VerificationEngine (P09)';
    if (eventType === 'ACTION_AUTHORIZED') return 'Approval Service';
    if (eventType === 'WEBHOOK_RECEIVED') return 'Recovery Engine';
    return actorType;
  };

  return (
    <div className="max-w-[1440px] mx-auto animate-in fade-in duration-300 flex flex-col pb-8">
      {/* Page Header */}
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-display font-bold text-[var(--color-text-primary)] mb-1">Audit</h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Trace recovery lifecycle events, decisions, execution, and verification evidence.
          </p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => refetch()} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors text-[var(--color-text-primary)]">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors text-[var(--color-text-primary)]">
            <Filter className="w-3.5 h-3.5" /> Filters
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-secondary)] transition-colors text-[var(--color-text-primary)]">
            <Download className="w-3.5 h-3.5" /> Export
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">AUDIT EVENTS</h3>
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.total.toLocaleString()}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">CASES WITH ACTIVITY</h3>
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.cases.toLocaleString()}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">APPROVAL EVENTS</h3>
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.approvalEvents.toLocaleString()}</div>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4 shadow-sm flex flex-col justify-between h-[80px]">
          <div className="flex justify-between items-start">
            <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)]">VERIFICATION EVENTS</h3>
          </div>
          <div className="text-2xl font-mono font-bold text-[var(--color-text-primary)]">{stats.verificationEvents.toLocaleString()}</div>
        </div>
      </div>

      {/* Filter Row */}
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-2 mb-6 flex gap-2 items-center text-xs">
        <input 
          type="text" 
          placeholder="Search case ID, event ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-[var(--color-bg)] border border-[var(--color-border)] rounded px-3 py-1.5 focus:outline-none focus:border-[var(--color-primary)] w-64 text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)]"
        />
        <button className="px-3 py-1.5 bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)]">Case</button>
        <button className="px-3 py-1.5 bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)]">Event Type</button>
        <button className="px-3 py-1.5 bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)]">Actor</button>
        <button className="px-3 py-1.5 bg-[var(--color-bg)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-surface-secondary)]">Status</button>
        <div className="ml-auto text-[var(--color-text-secondary)] uppercase tracking-wider font-bold text-[10px] px-2">SORT Newest first ▾</div>
      </div>

      {/* Main Content Split */}
      <div className="flex flex-col lg:flex-row gap-6 items-start">
        
        {/* Left Pane: Queue */}
        <div className="flex-1 lg:w-[65%] shrink-0 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-[var(--color-border)] bg-[var(--color-bg)]">
            <h2 className="font-bold text-sm text-[var(--color-text-primary)]">Audit Events</h2>
            <div className="text-xs text-[var(--color-text-muted)]">Recorded recovery lifecycle transitions</div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                  <th className="px-4 py-3 font-medium">TIME</th>
                  <th className="px-4 py-3 font-medium">EVENT ID</th>
                  <th className="px-4 py-3 font-medium">CASE</th>
                  <th className="px-4 py-3 font-medium">EVENT</th>
                  <th className="px-4 py-3 font-medium">ACTOR</th>
                  <th className="px-4 py-3 font-medium">COMPONENT</th>
                  <th className="px-4 py-3 font-medium">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2" />
                      Loading audit events...
                    </td>
                  </tr>
                ) : filteredEvents.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center text-[var(--color-text-muted)]">
                      No audit events match the current filters.
                    </td>
                  </tr>
                ) : (
                  filteredEvents.map((e: any) => {
                    const isSelected = selectedEventId === e.audit_event_id;
                    const date = new Date(e.timestamp);
                    const timeString = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
                    const shortCaseId = e.case_id ? `RC-${e.case_id.slice(0, 4)}` : 'N/A';
                    const component = getComponent(e.actor.type, e.event_type);
                    const isVerified = e.event_type === 'VERIFICATION_COMPLETED' && e.metadata?.verified_state === 'SUCCESS';
                    
                    return (
                      <tr 
                        key={e.audit_event_id}
                        onClick={() => setSelectedEventId(e.audit_event_id)}
                        className={`group cursor-pointer transition-colors ${
                          isSelected 
                            ? 'bg-[var(--color-primary)]/5 border-l-2 border-l-[var(--color-primary)]' 
                            : 'hover:bg-[var(--color-surface-secondary)] border-l-2 border-l-transparent'
                        }`}
                      >
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="font-mono text-xs text-[var(--color-text-secondary)]">{timeString}</div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="font-mono text-xs text-[var(--color-primary)]">{e.audit_event_id.replace('audit_','EVT-').toUpperCase().slice(0, 9)}</div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="font-mono text-xs text-[var(--color-text-primary)]">{shortCaseId}</div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="text-xs text-[var(--color-text-primary)] truncate max-w-[140px] capitalize">
                            {formatEventName(e.event_type)}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="text-xs text-[var(--color-text-secondary)] truncate max-w-[100px]">
                            {e.actor.id === 'SYSTEM' || e.actor.type === 'SYSTEM' ? 'System' : e.actor.id || e.actor.type}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <div className="text-xs text-[var(--color-text-secondary)] truncate max-w-[140px]">
                            {component}
                          </div>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          {isVerified ? (
                            <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/30">VERIFIED</span>
                          ) : (
                            <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-[var(--color-bg)] text-[var(--color-text-muted)] border border-[var(--color-border)]">RECORDED</span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Pane: Selected Detail */}
        <div className="flex-1 lg:w-[35%] shrink-0 sticky top-6 self-start">
          {selectedEvent ? (
            <SelectedEventPanel event={selectedEvent} allEvents={events} />
          ) : (
            <div className="h-full bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl flex items-center justify-center p-8 text-center">
              <div className="text-sm text-[var(--color-text-muted)]">
                Select an event to view details.
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Audit Boundary Banner */}
      <div className="mt-8 flex items-center justify-between p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
        <div className="flex items-center gap-3">
          <div className="bg-[var(--color-bg)] border border-[var(--color-border)] text-[10px] uppercase font-bold tracking-wider text-[var(--color-text-muted)] px-3 py-1 rounded">AUDIT BOUNDARY</div>
          <div className="text-xs text-[var(--color-text-muted)]">
            Important recovery lifecycle transitions are recorded in the audit timeline. Technical evidence is available where applicable.
          </div>
        </div>
        <button className="text-xs font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] flex items-center gap-1 transition-colors">
          View Integrity Report <ArrowRight className="w-3 h-3" />
        </button>
      </div>

    </div>
  );
}

function SelectedEventPanel({ event, allEvents }: { event: any, allEvents: any[] }) {
  const timeStr = new Date(event.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' UTC';
  
  const component = event.event_type === 'ACTION_EXECUTING' || event.event_type === 'RAZORPAY_REQUEST_COMPLETED' ? 'RecoveryActionService' :
                    event.event_type === 'POLICY_DECISION_CREATED' ? 'PolicyEngine' :
                    event.event_type === 'LLM_RECOMMENDATION_CREATED' ? 'Gemini' :
                    event.event_type.startsWith('VERIFICATION_') || event.event_type.startsWith('RECOVERY_') ? 'VerificationEngine (P09)' :
                    event.event_type === 'ACTION_AUTHORIZED' ? 'Approval Service' :
                    event.event_type === 'WEBHOOK_RECEIVED' ? 'Recovery Engine' :
                    event.actor.type;

  const actorStr = event.actor.id === 'SYSTEM' || event.actor.type === 'SYSTEM' ? 'SYSTEM' : event.actor.id || event.actor.type;
  
  // Historical Recovery Context
  const isExecution = event.event_type === 'ACTION_EXECUTING';
  const isApproval = event.event_type === 'ACTION_AUTHORIZED';
  const actionType = event.metadata?.action_type || event.metadata?.recommended_action || 'N/A';
  const amountMinor = event.metadata?.expected_recovery_amount;
  const amountStr = amountMinor ? `₹${(amountMinor/100).toLocaleString('en-US', {minimumFractionDigits:0})} INR` : 'N/A'; // Mocking INR for historical

  return (
    <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl shadow-sm flex flex-col overflow-hidden text-sm">
      
      {/* Header & Basic Info */}
      <div className="p-5 border-b border-[var(--color-border-subtle)]">
        <div className="flex justify-between items-start mb-1">
          <h2 className="font-bold text-[var(--color-text-primary)] text-base">Event Details</h2>
          <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded bg-[var(--color-bg)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">RECORDED</span>
        </div>
        <div className="font-mono text-sm text-[var(--color-primary)] mb-5">{event.audit_event_id.replace('audit_','EVT-').toUpperCase().slice(0, 9)}</div>
        
        <div className="grid grid-cols-[80px_1fr] gap-y-3 text-xs">
          <div className="text-[var(--color-text-secondary)]">Type</div>
          <div className="text-[var(--color-text-primary)] break-all">{event.event_type}</div>
          <div className="text-[var(--color-text-secondary)]">Actor</div>
          <div className="text-[var(--color-text-primary)]">{actorStr}</div>
          <div className="text-[var(--color-text-secondary)]">Component</div>
          <div className="text-[var(--color-text-primary)]">{component}</div>
          <div className="text-[var(--color-text-secondary)]">Time</div>
          <div className="font-mono text-[var(--color-text-primary)]">{timeStr}</div>
        </div>
      </div>

      {/* Recovery Context */}
      <div className="p-5 bg-[var(--color-bg)] border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-4">RECOVERY CONTEXT</h3>
        
        <div className="grid grid-cols-[80px_1fr] gap-y-3 text-xs">
          <div className="text-[var(--color-text-secondary)]">Action</div>
          <div className="text-[var(--color-text-primary)] truncate">{actionType}</div>
          <div className="text-[var(--color-text-secondary)]">Amount</div>
          <div className="text-[var(--color-text-primary)]">{amountStr}</div>
          <div className="text-[var(--color-text-secondary)]">Auth</div>
          <div className={`${isApproval || isExecution ? 'text-[var(--color-success)]' : 'text-[var(--color-text-muted)]'}`}>{isApproval || isExecution ? 'APPROVED' : 'N/A'}</div>
          <div className="text-[var(--color-text-secondary)]">Provider</div>
          <div className="text-[var(--color-text-primary)]">{isExecution ? 'Razorpay Test' : 'N/A'}</div>
          <div className="text-[var(--color-text-secondary)]">Verification</div>
          <div className="text-[var(--color-warning)] font-medium">PENDING</div>
        </div>
      </div>

      {/* Lifecycle Trace */}
      <div className="p-5 border-b border-[var(--color-border-subtle)]">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-4">LIFECYCLE TRACE</h3>
        
        <div className="space-y-4 relative before:absolute before:left-[7px] before:top-2 before:bottom-2 before:w-[2px] before:bg-[var(--color-border-subtle)]">
          {allEvents.filter(e => e.case_id === event.case_id).sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()).map((e, i) => (
            <div key={e.audit_event_id} className="flex items-center gap-3 relative z-10">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${e.audit_event_id === event.audit_event_id ? 'bg-[var(--color-primary)]' : 'bg-[var(--color-border)]'}`}>
                {e.audit_event_id === event.audit_event_id && <div className="w-1.5 h-1.5 bg-[var(--color-bg)] rounded-full"></div>}
              </div>
              <span className={`text-xs ${e.audit_event_id === event.audit_event_id ? 'text-[var(--color-primary)] font-bold' : 'text-[var(--color-text-primary)]'}`}>
                {e.event_type}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Actor Trace */}
      <div className="p-5">
        <h3 className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)] mb-4">ACTOR TRACE</h3>
        
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span className="px-2 py-1 text-[10px] font-mono bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded text-[var(--color-text-secondary)]">Gemini</span>
          <ArrowRight className="w-3 h-3 text-[var(--color-border)]" />
          <span className="px-2 py-1 text-[10px] font-mono bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded text-[var(--color-text-secondary)]">PolicyEngine</span>
          <ArrowRight className="w-3 h-3 text-[var(--color-border)]" />
          <span className="px-2 py-1 text-[10px] font-mono bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded text-[var(--color-text-secondary)]">Human Operator</span>
          <ArrowRight className="w-3 h-3 text-[var(--color-border)]" />
          <span className="px-2 py-1 text-[10px] font-mono bg-[var(--color-primary)]/10 border border-[var(--color-primary)]/30 rounded text-[var(--color-primary)] font-bold">RecoveryActionService</span>
        </div>

        <div className="text-[10px] italic text-[var(--color-text-muted)] leading-relaxed">
          Components shown reflect recorded lifecycle transitions; they are not independent execution authorities.
        </div>
      </div>

    </div>
  );
}
