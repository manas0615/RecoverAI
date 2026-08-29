import { useMemo } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { useCases } from '../hooks/useCases';
import { AccessBoundary } from '../components/feedback/AccessBoundary';
import { MetricCard } from '../components/data-display/MetricCard';
import { UnavailableMetric } from '../components/data-display/UnavailableMetric';
import { CaseTable } from '../components/data-display/CaseTable';
import { MoneyValue } from '../components/financial/MoneyValue';

export function Dashboard() {
  const { data, loading, error, refetch } = useCases();

  const metrics = useMemo(() => {
    if (!data) return { activeCases: 0, revenueAtRisk: {}, openCases: [] };
    
    const open = data.cases.filter(c => c.status === 'OPEN');
    const revenueByCurrency = open.reduce((acc, c) => {
      acc[c.currency] = (acc[c.currency] || 0) + c.amount_minor;
      return acc;
    }, {} as Record<string, number>);

    return {
      activeCases: open.length,
      revenueAtRisk: revenueByCurrency,
      openCases: open
    };
  }, [data]);

  if (error) {
    return <AccessBoundary error={error} onRetry={refetch} fallbackMessage="Unable to load recovery data." />;
  }

  // Handle multi-currency for the hero metric
  // If multiple currencies exist, we show a breakdown or just primary if only one.
  const currencies = Object.keys(metrics.revenueAtRisk);
  const revenueDisplay = currencies.length > 0 ? (
    <div className="flex flex-col gap-1">
      {currencies.map(curr => (
        <MoneyValue key={curr} amountMinor={metrics.revenueAtRisk[curr]} currency={curr} />
      ))}
    </div>
  ) : (
    <MoneyValue amountMinor={0} currency="INR" />
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader 
        title="Overview" 
        subtitle="Revenue recovery operations"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          label="Open Revenue at Risk" 
          value={loading ? <div className="h-9 w-24 bg-[var(--color-surface-secondary)] rounded animate-pulse" /> : revenueDisplay}
        />
        <MetricCard 
          label="Active Cases" 
          value={loading ? <div className="h-9 w-12 bg-[var(--color-surface-secondary)] rounded animate-pulse" /> : metrics.activeCases}
        />
        
        {/* Visually secondary unavailable metrics per architectural plan */}
        <UnavailableMetric label="Verified Recovered" />
        <UnavailableMetric label="Recovery Rate" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h3 className="text-sm font-medium text-[var(--color-text-primary)] mb-2">Open Recovery Cases</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Currently tracking <strong className="text-[var(--color-text-primary)]">{metrics.activeCases}</strong> active cases in the recovery pipeline.
          </p>
        </div>
        
        <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h3 className="text-sm font-medium text-[var(--color-text-primary)] mb-4">System Health</h3>
          <div className="flex items-center gap-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-success)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--color-success)]"></span>
            </span>
            <span className="text-sm font-medium text-[var(--color-text-secondary)]">System Operational</span>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)]">Recent Recovery Cases</h2>
        <CaseTable cases={data?.cases.slice(0, 10) || []} loading={loading} />
      </div>
    </div>
  );
}
