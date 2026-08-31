import { useState, useMemo } from 'react';
import { useCases, useAnalytics } from '../hooks/useApi';
import { AccessBoundary } from '../components/feedback/AccessBoundary';
import { CaseTable } from '../components/data-display/CaseTable';
import { MetricCard } from '../components/data-display/MetricCard';
import { AlertTriangle, RefreshCw, Filter, Download, Search } from 'lucide-react';

export function CaseList() {
  const { data: casesData, loading: casesLoading, error: casesError, refetch: refetchCases } = useCases();
  const { data: analyticsData, loading: analyticsLoading } = useAnalytics();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [failureFilter, setFailureFilter] = useState('All');
  const [stageFilter, setStageFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  
  const [page, setPage] = useState(1);
  const pageSize = 5;

  const handleRefresh = () => {
    refetchCases();
  };

  const filteredCases = useMemo(() => {
    if (!casesData?.cases) return [];
    let filtered = casesData.cases;

    if (search.trim()) {
      const q = search.toLowerCase();
      filtered = filtered.filter(c => 
        c.case_id.toLowerCase().includes(q) || 
        (c.failure_code && c.failure_code.toLowerCase().includes(q))
      );
    }

    if (statusFilter !== 'All') {
      filtered = filtered.filter(c => {
        const derivedStatus = c.workflow_state === 'WAITING_APPROVAL' ? 'Approval Required' : 
                              (c.outcome_type === 'RECOVERED' ? 'Recovered' : 
                              (c.workflow_state === 'EXECUTING' ? 'Executing' : 
                              (c.workflow_state === 'ESCALATED' ? 'Escalated' : c.status)));
        return derivedStatus === statusFilter;
      });
    }

    if (failureFilter !== 'All') {
      filtered = filtered.filter(c => c.failure_code === failureFilter);
    }

    if (stageFilter !== 'All') {
      filtered = filtered.filter(c => {
        const stage = c.workflow_state === 'WAITING_APPROVAL' || c.workflow_state === 'ESCALATED' ? 'Human Approval' :
                      c.workflow_state === 'POLICY_REVIEW' ? 'Policy Review' :
                      c.workflow_state === 'EXECUTING' ? 'Execution' :
                      c.workflow_state === 'VERIFYING' ? 'Verification' :
                      c.workflow_state === 'VERIFIED_SUCCESS' || c.outcome_type === 'RECOVERED' ? 'Verified' : 'Unknown';
        return stage === stageFilter;
      });
    }
    
    if (riskFilter !== 'All') {
      filtered = filtered.filter(c => {
        const risk = c.amount_minor > 1000000 ? 'High' : 'Normal';
        return risk === riskFilter;
      });
    }

    return filtered;
  }, [casesData, search, statusFilter, failureFilter, stageFilter, riskFilter]);

  const totalPages = Math.ceil(filteredCases.length / pageSize);
  const currentCases = filteredCases.slice((page - 1) * pageSize, page * pageSize);

  // Reset page when filters change
  useMemo(() => {
    setPage(1);
  }, [search, statusFilter, failureFilter, stageFilter, riskFilter]);

  if (casesError) {
    return <AccessBoundary error={casesError} onRetry={handleRefresh} fallbackMessage="Unable to load recovery cases." />;
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-[var(--color-text-primary)]">Recovery Cases</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            Monitor revenue risk, recovery decisions, execution state, and cases requiring attention.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={handleRefresh} className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-sm font-medium hover:bg-[var(--color-surface-secondary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-sm font-medium hover:bg-[var(--color-surface-secondary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">
            <Filter className="w-4 h-4" />
            Filters
          </button>
          <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-sm font-medium hover:bg-[var(--color-surface-secondary)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] opacity-50 cursor-not-allowed" title="Export temporarily disabled">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          label="OPEN CASES" 
          value={analyticsLoading ? '...' : analyticsData?.active_cases || 0}
        />
        <MetricCard 
          label="AT RISK" 
          value={analyticsLoading ? '...' : `₹${((analyticsData?.revenue_at_risk?.INR || 0) / 100).toLocaleString()}`}
          labelColor="text-[var(--color-warning)]"
          icon={<AlertTriangle className="w-4 h-4 text-[var(--color-warning)]" />}
        />
        <MetricCard 
          label="AWAITING APPROVAL" 
          value={analyticsLoading ? '...' : analyticsData?.awaiting_approval || 0}
        />
        <MetricCard 
          label="IN EXECUTION" 
          value={analyticsLoading ? '...' : analyticsData?.in_execution || 0}
          labelColor="text-[var(--color-primary)]"
        />
      </div>

      <div className="flex flex-col lg:flex-row gap-4 p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
          <input 
            type="text" 
            placeholder="Search case ID, failure code..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg pl-9 pr-4 py-2 text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
          />
        </div>
        
        <div className="flex flex-wrap lg:flex-nowrap gap-3">
          <select 
            className="bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-secondary)] focus:outline-none focus:border-[var(--color-primary)] appearance-none cursor-pointer pr-8"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
          >
            <option value="All">Status: All</option>
            <option value="Approval Required">Approval Required</option>
            <option value="Executing">Executing</option>
            <option value="Recovered">Recovered</option>
            <option value="Escalated">Escalated</option>
            <option value="OPEN">Open</option>
          </select>
          
          <select 
            className="bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-secondary)] focus:outline-none focus:border-[var(--color-primary)] appearance-none cursor-pointer pr-8"
            value={failureFilter}
            onChange={e => setFailureFilter(e.target.value)}
          >
            <option value="All">Failure Cause: All</option>
            <option value="PAYMENT_LINK_CAPTURE_FAILED">PAYMENT_LINK_CAPTURE_FAILED</option>
            <option value="PAYMENT_LINK_EXPIRED">PAYMENT_LINK_EXPIRED</option>
            <option value="CUSTOMER_ERROR">CUSTOMER_ERROR</option>
            <option value="INSUFFICIENT_FUNDS">INSUFFICIENT_FUNDS</option>
          </select>
          
          <select 
            className="bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-secondary)] focus:outline-none focus:border-[var(--color-primary)] appearance-none cursor-pointer pr-8"
            value={stageFilter}
            onChange={e => setStageFilter(e.target.value)}
          >
            <option value="All">Recovery Stage: All</option>
            <option value="Human Approval">Human Approval</option>
            <option value="Policy Review">Policy Review</option>
            <option value="Execution">Execution</option>
            <option value="Verification">Verification</option>
            <option value="Verified">Verified</option>
          </select>
          
          <select 
            className="bg-[var(--color-bg)] border border-[var(--color-border-subtle)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-secondary)] focus:outline-none focus:border-[var(--color-primary)] appearance-none cursor-pointer pr-8"
            value={riskFilter}
            onChange={e => setRiskFilter(e.target.value)}
          >
            <option value="All">Risk Level: All</option>
            <option value="Normal">Normal</option>
            <option value="High">High</option>
          </select>
        </div>
      </div>

      <CaseTable cases={currentCases} loading={casesLoading} />

      {!casesLoading && filteredCases.length > 0 && (
        <div className="flex items-center justify-between px-4 py-3 border border-[var(--color-border)] rounded-xl bg-[var(--color-surface)] shadow-sm text-sm text-[var(--color-text-secondary)]">
          <div>
            Showing {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, filteredCases.length)} of {filteredCases.length} case{filteredCases.length !== 1 ? "s" : ""}
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-1.5 border border-[var(--color-border)] rounded bg-[var(--color-surface)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-1.5 border border-[var(--color-border)] rounded bg-[var(--color-surface)] text-[var(--color-text-primary)] hover:bg-[var(--color-surface-secondary)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
