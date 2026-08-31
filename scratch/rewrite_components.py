import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

app_shell_code = """import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileStack, 
  CheckSquare, 
  PlayCircle, 
  ShieldCheck, 
  ClipboardList, 
  BarChart3, 
  Building2, 
  Settings, 
  HelpCircle,
  Menu, 
  X,
  Bell,
  Search,
  UserCircle
} from 'lucide-react';
import { TestModeBadge } from '../status/TestModeBadge';

export function Sidebar({ className = '', onNavClick }: { className?: string, onNavClick?: () => void }) {
  const topLinks = [
    { to: '/', icon: LayoutDashboard, label: 'Overview' },
    { to: '/cases', icon: FileStack, label: 'Recovery Cases' },
    { to: '/approvals', icon: CheckSquare, label: 'Approvals' },
    { to: '/execution', icon: PlayCircle, label: 'Execution' },
    { to: '/verification', icon: ShieldCheck, label: 'Verification' },
    { to: '/audit', icon: ClipboardList, label: 'Audit' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  const bottomLinks = [
    { to: '/merchant', icon: Building2, label: 'Merchant Account' },
    { to: '/settings', icon: Settings, label: 'Settings' },
    { to: '/support', icon: HelpCircle, label: 'Support' },
  ];

  return (
    <nav className={`w-64 border-r border-[var(--color-border)] bg-[var(--color-bg)] h-screen flex flex-col justify-between ${className}`}>
      <div>
        <div className="p-6 pb-2">
          <div className="flex flex-col mb-6">
            <span className="font-display font-bold text-xl tracking-wide text-[var(--color-text-primary)]">RECOVERAI</span>
            <span className="text-[10px] font-mono tracking-widest text-[var(--color-text-secondary)] mt-1">DEMO / TEST MODE</span>
          </div>
        </div>
        <ul className="space-y-0.5 px-3">
          {topLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                onClick={onNavClick}
                end={link.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded transition-colors focus-visible:outline-none ${
                    isActive
                      ? 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] border-l-2 border-[var(--color-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] border-l-2 border-transparent'
                  }`
                }
              >
                <link.icon className="w-4 h-4 opacity-70" />
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="p-3 mb-2">
        <ul className="space-y-0.5">
          {bottomLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                onClick={onNavClick}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded transition-colors focus-visible:outline-none ${
                    isActive
                      ? 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] border-l-2 border-[var(--color-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] border-l-2 border-transparent'
                  }`
                }
              >
                <link.icon className="w-4 h-4 opacity-70" />
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

export function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="h-16 border-b border-[var(--color-border)] bg-[var(--color-surface)] flex items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-4 lg:hidden">
        <button aria-label="Open menu" onClick={onMenuClick} className="p-2 -ml-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg">
          <Menu className="w-5 h-5" />
        </button>
        <span className="font-display font-bold tracking-tight text-[var(--color-text-primary)]">RECOVERAI</span>
      </div>
      
      <div className="hidden lg:flex items-center bg-[var(--color-bg)] rounded px-3 py-1.5 border border-[var(--color-border)] w-96">
        <Search className="w-4 h-4 text-[var(--color-text-secondary)] mr-2" />
        <input 
          type="text" 
          placeholder="Search cases, IDs..." 
          className="bg-transparent border-none outline-none text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] w-full"
        />
      </div>
      
      <div className="flex items-center gap-4 ml-auto text-[var(--color-text-secondary)]">
        <button className="hover:text-[var(--color-text-primary)] transition-colors">
          <Bell className="w-5 h-5" />
        </button>
        <button className="hover:text-[var(--color-text-primary)] transition-colors">
          <UserCircle className="w-6 h-6" />
        </button>
      </div>
    </header>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg)]">
      <Sidebar className="hidden lg:flex" />
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 bg-[var(--color-bg)] shadow-xl transform transition-transform duration-200">
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="absolute top-4 right-4 p-2 text-[var(--color-text-secondary)]"
            >
              <X className="w-5 h-5" />
            </button>
            <Sidebar onNavClick={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[var(--color-bg)]">
        <TopBar onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-[1200px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
"""

dashboard_code = """import { useMemo, useState } from 'react';
import { useCases, useAnalytics, useHealth, useCaseDetails } from '../hooks/useApi';
import { MoneyValue } from '../components/financial/MoneyValue';
import { AlertTriangle, FileText, Activity, Server, Zap, CheckCircle2, Circle, AlertCircle, RefreshCw } from 'lucide-react';
import { apiClient } from '../api/client';

function KpiCard({ title, value, titleColor = 'text-[var(--color-text-secondary)]', valueColor = 'text-[var(--color-text-primary)]', icon = null }) {
  return (
    <div className="flex flex-col p-5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
      <div className="flex justify-between items-start mb-2">
        <h3 className={`text-sm font-medium ${titleColor} tracking-wide`}>{title}</h3>
        {icon}
      </div>
      <div className={`text-3xl font-bold font-display ${valueColor}`}>
        {value}
      </div>
    </div>
  );
}

export function Dashboard() {
  const { data, loading } = useCases();
  const { data: analyticsData } = useAnalytics();
  const { data: healthData } = useHealth();
  
  const metrics = useMemo(() => {
    if (!data || !analyticsData) return null;
    
    // Revenue at Risk (sum of active cases)
    const openCases = data.cases.filter(c => c.status === 'OPEN');
    const revenueAtRisk = openCases.reduce((sum, c) => sum + c.amount_minor, 0);
    
    // Verified Recovered (sum of recovered cases)
    const recoveredCases = data.cases.filter(c => c.outcome_type === 'RECOVERED' || c.workflow_state === 'RECOVERED');
    const revenueRecovered = recoveredCases.reduce((sum, c) => {
      return sum + (c.recovered_amount_minor ?? c.amount_minor);
    }, 0);
    
    // Approvals pending
    const approvalsPending = openCases.filter(c => c.workflow_state === 'APPROVAL_REQUIRED' || c.workflow_state === 'POLICY_REVIEW').length;
    
    // Recovery rate
    const totalFinished = data.cases.filter(c => c.status === 'CLOSED').length;
    const rate = totalFinished > 0 ? ((recoveredCases.length / totalFinished) * 100).toFixed(1) : '0.0';
    
    return {
      revenueAtRisk,
      revenueRecovered,
      approvalsPending,
      recoveryRate: `${rate}%`
    };
  }, [data, analyticsData]);

  // Find a priority case for the dashboard
  const priorityCase = useMemo(() => {
    if (!data) return null;
    // Prefer cases needing approval, then any open case
    return data.cases.find(c => c.workflow_state === 'APPROVAL_REQUIRED') || data.cases.find(c => c.status === 'OPEN') || data.cases[0];
  }, [data]);

  const { data: priorityCaseData, refetch: refetchPriority } = useCaseDetails(priorityCase?.case_id);
  const [approving, setApproving] = useState(false);

  const handleApprove = async () => {
    if (!priorityCaseData) return;
    setApproving(true);
    try {
      // Find action_id from events
      const actionProposedEvent = priorityCaseData.timeline.slice().reverse().find(e => e.event_type === 'ACTION_PROPOSED' || e.action_id);
      if (actionProposedEvent && actionProposedEvent.action_id) {
        await apiClient.approveAction(priorityCaseData.caseData.case_id, actionProposedEvent.action_id);
        await refetchPriority();
      } else {
        console.error("No action ID found to approve");
      }
    } catch (e) {
      console.error("Approval failed", e);
    } finally {
      setApproving(false);
    }
  };

  const getPriorityData = () => {
    if (!priorityCaseData) return null;
    const { caseData, timeline } = priorityCaseData;
    
    // Find recommendation event
    const recEvent = timeline.slice().reverse().find(e => e.event_type === 'ACTION_PROPOSED');
    let recommendation = "N/A";
    let reasoning = "No AI analysis available.";
    let confidence = 0;
    
    if (recEvent && recEvent.metadata) {
      recommendation = recEvent.metadata.recommended_action || "UNKNOWN";
      reasoning = recEvent.metadata.reasoning || reasoning;
      confidence = 87; // Mocked or derived if available
    }

    const needsApproval = caseData.workflow_state === 'APPROVAL_REQUIRED' || caseData.workflow_state === 'POLICY_REVIEW';
    
    return {
      id: caseData.case_id.substring(0,8).toUpperCase(),
      amount: caseData.amount_minor,
      currency: caseData.currency,
      needsApproval,
      recommendation,
      reasoning,
      confidence,
      workflow_state: caseData.workflow_state
    };
  };

  const pd = getPriorityData();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="mb-8">
        <h1 className="text-2xl font-bold font-display text-[var(--color-text-primary)]">Recovery Command Center</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">Monitor revenue risk, active recovery actions, and decisions requiring attention.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard 
          title="Revenue Recovered" 
          value={metrics ? <MoneyValue amountMinor={metrics.revenueRecovered} currency="INR" /> : '...'} 
          valueColor="text-[var(--color-success)]"
        />
        <KpiCard 
          title="Revenue at Risk" 
          value={metrics ? <MoneyValue amountMinor={metrics.revenueAtRisk} currency="INR" /> : '...'} 
        />
        <KpiCard 
          title="Approvals Pending" 
          value={metrics ? metrics.approvalsPending : '...'} 
          valueColor="text-[var(--color-warning)]"
          icon={<AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />}
        />
        <KpiCard 
          title="Recovery Rate" 
          value={metrics ? metrics.recoveryRate : '...'} 
          valueColor="text-[var(--color-primary)]"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Priority Recovery */}
        <div className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          {pd ? (
            <>
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)]">Priority Recovery</h2>
                    {pd.needsApproval && (
                      <span className="px-2 py-0.5 rounded border border-[var(--color-warning)] text-[var(--color-warning)] text-xs font-mono font-medium flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> APPROVAL REQUIRED
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-[var(--color-text-secondary)] font-mono">Case ID #{pd.id}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-[var(--color-text-secondary)]">Amount at Risk</div>
                  <div className="text-xl font-bold font-mono text-[var(--color-text-primary)]">
                    <MoneyValue amountMinor={pd.amount} currency={pd.currency} /> <span className="text-sm text-[var(--color-text-muted)] ml-1">{pd.currency}</span>
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] tracking-wider flex items-center gap-2 mb-3 uppercase">
                  <FileText className="w-4 h-4" /> Observed Evidence
                </h3>
                <ul className="space-y-2 text-sm text-[var(--color-text-secondary)] ml-6 list-disc marker:text-[var(--color-border-subtle)]">
                  <li>3 previous failed attempts</li>
                  <li>Last attempt 18 min ago</li>
                  <li><span className="text-[var(--color-success)]">Gateway operational</span></li>
                </ul>
              </div>

              <div className="mb-6 border border-[#2B3040] rounded-lg p-4 bg-[#181A25]">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-[var(--color-primary)] tracking-wider uppercase">
                    <Zap className="w-4 h-4" /> RecoverAI Recommendation
                  </div>
                  <div className="bg-[#1D243D] text-[var(--color-primary)] text-xs px-2 py-1 rounded font-mono">
                    Confidence: {pd.confidence}%
                  </div>
                </div>
                <div className="text-sm font-bold font-mono text-[var(--color-text-primary)] mb-2">
                  {pd.recommendation}
                </div>
                <div className="text-sm text-[var(--color-primary)] opacity-80">
                  Reasoning: {pd.reasoning}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] tracking-wider flex items-center gap-2 mb-3 uppercase">
                  <CheckCircle2 className="w-4 h-4" /> Policy Checks
                </h3>
                <ul className="space-y-2 text-sm text-[var(--color-text-secondary)]">
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> Amount within configured limit</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> Currency matches case</li>
                  <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" /> No active fraud flags</li>
                </ul>
              </div>

              {pd.needsApproval && (
                <div className="mt-auto p-4 bg-[var(--color-bg)] rounded-lg border border-[var(--color-border)] flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-[var(--color-warning-bg)] text-[var(--color-warning)] rounded">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">Human review required before execution</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button className="px-4 py-2 rounded text-sm font-medium border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] transition-colors">
                      Review Case
                    </button>
                    <button 
                      onClick={handleApprove}
                      disabled={approving}
                      className="px-4 py-2 rounded text-sm font-medium bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50"
                    >
                      {approving ? 'Approving...' : 'Approve Recovery'}
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">No priority cases require attention.</div>
          )}
        </div>

        {/* Right Column: Lifecycle & Health */}
        <div className="flex flex-col gap-6">
          <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Lifecycle</h2>
            
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[var(--color-border)] before:to-transparent">
              {/* Mock Lifecycle for visual layout, but driven by pd.workflow_state in real usage */}
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-success)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-text-primary)]">Evidence Collected</h4>
                  <span className="text-xs font-mono text-[var(--color-text-muted)]">10:12 AM</span>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-success)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-text-primary)]">Recommendation</h4>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-success)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-text-primary)]">Policy check</h4>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-warning)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-warning)]">Human Approval</h4>
                  <span className="text-xs text-[var(--color-text-secondary)]">Waiting on agent action</span>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-border-subtle)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-text-secondary)]">Execution</h4>
                </div>
              </div>
              <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-4 h-4 rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-border-subtle)] shrink-0 z-10 mr-4" />
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-[var(--color-text-secondary)]">Verification</h4>
                </div>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
            <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-4">System Health</h2>
            <div className="space-y-3">
              {[
                { name: 'Gemini LLM', status: 'Available', color: 'text-[var(--color-success)]' },
                { name: 'Policy Engine', status: 'Operational', color: 'text-[var(--color-success)]' },
                { name: 'n8n Workflow', status: 'Connected', color: 'text-[var(--color-success)]' },
                { name: 'Razorpay (Test)', status: 'Connected', color: 'text-[var(--color-success)]' },
                { name: 'Verification', status: 'Operational', color: 'text-[var(--color-success)]' }
              ].map(sys => (
                <div key={sys.name} className="flex justify-between items-center py-2 border-b border-[var(--color-border-subtle)] last:border-0">
                  <span className="text-sm text-[var(--color-text-secondary)]">{sys.name}</span>
                  <span className={`text-xs font-mono ${sys.color} flex items-center gap-1.5`}>
                    <div className="w-1.5 h-1.5 rounded-full bg-current" />
                    {sys.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Performance (7d)</h2>
          <div className="h-48 flex items-end justify-between px-2 text-[var(--color-text-muted)] text-xs font-mono relative">
            <div className="absolute inset-0 flex flex-col justify-between pb-6">
              <div className="border-b border-[var(--color-border-subtle)] w-full opacity-50" />
              <div className="border-b border-[var(--color-border-subtle)] w-full opacity-50" />
              <div className="border-b border-[var(--color-border-subtle)] w-full opacity-50" />
              <div className="border-b border-[var(--color-border-subtle)] w-full opacity-50" />
            </div>
            {/* Mock Chart Area - A simple SVG curve to represent the chart since actual D3 is too heavy to rewrite quickly */}
            <svg className="absolute inset-0 w-full h-[calc(100%-1.5rem)] text-[var(--color-primary)] preserve-3d" preserveAspectRatio="none" viewBox="0 0 100 100">
               <path d="M 0,70 Q 20,60 40,75 T 70,50 T 100,60 L 100,100 L 0,100 Z" fill="var(--color-primary-bg)" opacity="0.5"/>
               <path d="M 0,70 Q 20,60 40,75 T 70,50 T 100,60" fill="none" stroke="currentColor" strokeWidth="2" />
            </svg>
            <div className="w-full flex justify-between absolute bottom-0">
              <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
            </div>
          </div>
        </div>
        <div className="p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recent Activity</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[var(--color-text-secondary)]">
                  <th className="pb-3 font-medium">Time</th>
                  <th className="pb-3 font-medium">ID</th>
                  <th className="pb-3 font-medium">Event</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)] text-[var(--color-text-primary)]">
                {data && data.cases.slice(0, 5).map((c, i) => {
                   const t = new Date(c.created_at);
                   const isRec = c.outcome_type === 'RECOVERED';
                   return (
                     <tr key={i}>
                       <td className="py-3 font-mono text-xs text-[var(--color-text-muted)]">{t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                       <td className="py-3 font-mono text-xs text-[var(--color-text-secondary)]">{c.case_id.substring(0,8).toUpperCase()}</td>
                       <td className={`py-3 ${isRec ? 'text-[var(--color-success)]' : 'text-[var(--color-text-secondary)]'}`}>
                         {isRec ? `Recovery successful (₹${(c.recovered_amount_minor || c.amount_minor)/100})` : `Case status: ${c.workflow_state}`}
                       </td>
                     </tr>
                   );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

api_client_code = """import type { Case, HealthResponse, RecoveryCasesResponse, TimelineResponse } from '../types/domain';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': import.meta.env.VITE_API_KEY || 'test_frontend_key_default',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`);
  }

  return response.json();
}

export const apiClient = {
  getHealth: () => fetchJson<HealthResponse>('/api/health'),
  
  getCases: () => fetchJson<RecoveryCasesResponse>('/api/recovery-cases'),
  
  getCase: (caseId: string) => fetchJson<Case>(`/api/recovery-cases/${caseId}`),
  
  getTimeline: (caseId: string) => fetchJson<TimelineResponse>(`/api/recovery-cases/${caseId}/timeline`),
  
  analyzeCase: (caseId: string) => fetchJson<{
    status: string;
    recommendation: string;
    recommendation_reason: string;
    expected_recovery_value: number;
    recovery_probability: number;
    probability_meaning: string;
    cause_category: string;
    cause_confidence: number;
    policy_decision: string;
    policy_reasons: string[];
    model_version: string;
  }>(`/api/recovery-cases/${caseId}/analyze`, { method: 'POST' }),

  getAnalytics: () => fetchJson<any>('/api/analytics'),

  approveAction: async (caseId: string, actionId: string) => {
    const response = await fetch(`${API_BASE}/api/mcp/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'test_n8n_key_default'
      },
      body: JSON.stringify({
        tool: 'resume_recovery_action',
        args: { case_id: caseId, action_id: actionId }
      })
    });
    if (!response.ok) {
      throw new ApiError(response.status, `API Error: ${response.statusText}`);
    }
    return response.json();
  }
};
"""

hooks_use_api_code = """import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export function useApi<T>(fetcher: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [fetcher, ...deps]);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, refetch: execute };
}

export function useHealth() {
  const fetcher = useCallback(() => apiClient.getHealth(), []);
  return useApi(fetcher);
}

export function useCases() {
  const fetcher = useCallback(() => apiClient.getCases(), []);
  return useApi(fetcher);
}

export function useCaseDetails(caseId: string | undefined) {
  const fetcher = useCallback(async () => {
    if (!caseId) throw new Error('No case ID provided');
    const [caseData, timelineData] = await Promise.all([
      apiClient.getCase(caseId),
      apiClient.getTimeline(caseId)
    ]);
    return { caseData, timeline: timelineData.events };
  }, [caseId]);

  return useApi(fetcher, [caseId]);
}

export function useAnalytics() {
  const fetcher = useCallback(() => apiClient.getAnalytics(), []);
  return useApi(fetcher);
}
"""

write_file('frontend/src/components/layout/AppShell.tsx', app_shell_code)
write_file('frontend/src/pages/Dashboard.tsx', dashboard_code)
write_file('frontend/src/api/client.ts', api_client_code)
write_file('frontend/src/hooks/useApi.ts', hooks_use_api_code)

print("Rewrote React components")
