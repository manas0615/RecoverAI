import { useMemo } from 'react';
import { PageHeader } from '../components/layout/PageHeader';
import { useCases, useAnalytics } from '../hooks/useCases';
import { AccessBoundary } from '../components/feedback/AccessBoundary';
import { MetricCard } from '../components/data-display/MetricCard';
import { UnavailableMetric } from '../components/data-display/UnavailableMetric';
import { CaseTable } from '../components/data-display/CaseTable';
import { MoneyValue } from '../components/financial/MoneyValue';

const FunnelChart = ({ data }: { data: { stage: string; count: number }[] }) => {
  const maxCount = Math.max(...data.map(d => d.count), 1);
  return (
    <div className="flex flex-col gap-4 mt-2">
      {data.map((item, index) => {
        const width = `${(item.count / maxCount) * 100}%`;
        return (
          <div key={index} className="flex items-center gap-4">
            <div className="w-24 text-sm font-medium text-[var(--color-text-primary)] truncate" title={item.stage}>{item.stage}</div>
            <div className="flex-1 flex items-center">
              <div 
                className="h-8 rounded-r bg-[#D6C8B8] shadow-sm flex items-center justify-end px-3 transition-all duration-500 ease-out" 
                style={{ width, minWidth: item.count > 0 ? '2rem' : '0' }}
              >
                {item.count > 0 && <span className="text-xs font-semibold text-[#5C5046]">{item.count}</span>}
              </div>
              {item.count === 0 && <span className="ml-3 text-sm font-semibold text-[var(--color-text-secondary)]">0</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
};

const OutcomeDistribution = ({ data }: { data: { name: string; value: number }[] }) => {
  const total = data.reduce((acc, curr) => acc + curr.value, 0) || 1;
  return (
    <div className="flex flex-col gap-5 mt-2">
      {data.map((item, index) => {
        const percentage = ((item.value / total) * 100).toFixed(1);
        return (
          <div key={index} className="flex flex-col gap-1.5">
            <div className="flex justify-between text-sm">
              <span className="font-medium text-[var(--color-text-primary)]">{item.name}</span>
              <span className="font-semibold text-[var(--color-text-secondary)]">{percentage}% <span className="text-[var(--color-text-muted)] font-normal">({item.value})</span></span>
            </div>
            <div className="w-full bg-[var(--color-surface-secondary)] rounded-full h-2.5 shadow-inner">
              <div 
                className="bg-[#C8B49C] h-2.5 rounded-full transition-all duration-500 ease-out" 
                style={{ width: `${percentage}%` }} 
              />
            </div>
          </div>
        );
      })}
    </div>
  );
};

export function Dashboard() {
  const { data, loading, error, refetch } = useCases();
  const { data: analyticsData, loading: analyticsLoading, error: analyticsError, refetch: analyticsRefetch } = useAnalytics();

  const metrics = useMemo(() => {
    if (!data) return { activeCases: 0, revenueAtRisk: {}, verifiedRecovered: {}, openCases: [] };
    
    const open = data.cases.filter(c => c.status === 'OPEN');
    const revenueByCurrency = open.reduce((acc, c) => {
      acc[c.currency] = (acc[c.currency] || 0) + c.amount_minor;
      return acc;
    }, {} as Record<string, number>);

    const recoveredByCurrency = data.cases.reduce((acc, c) => {
      const isRecovered = c.outcome_type === 'RECOVERED' || c.outcome_type === 'SUCCESS' || c.workflow_state === 'RECOVERED' || (c.recovered_amount_minor !== undefined && c.recovered_amount_minor > 0);
      if (isRecovered) {
        const amt = c.recovered_amount_minor ?? c.amount_minor;
        if (amt > 0) {
          acc[c.currency] = (acc[c.currency] || 0) + amt;
        }
      }
      return acc;
    }, {} as Record<string, number>);

    return {
      activeCases: open.length,
      revenueAtRisk: revenueByCurrency,
      verifiedRecovered: recoveredByCurrency,
      openCases: open
    };
  }, [data]);

  if (error || analyticsError) {
    return <AccessBoundary error={error || analyticsError || new Error('Unknown')} onRetry={() => { refetch(); analyticsRefetch(); }} fallbackMessage="Unable to load recovery data." />;
  }

  const openCurrencies = Object.keys(metrics.revenueAtRisk);
  const revenueDisplay = (
    <div className="flex flex-col gap-1">
      {openCurrencies.map(curr => (
        <MoneyValue key={curr} amountMinor={metrics.revenueAtRisk[curr]} currency={curr} />
      ))}
    </div>
  );

  const recoveredCurrencies = Object.keys(metrics.verifiedRecovered);
  const recoveredDisplay = (
    <div className="flex flex-col gap-1">
      {recoveredCurrencies.map(curr => (
        <MoneyValue key={curr} amountMinor={metrics.verifiedRecovered[curr]} currency={curr} />
      ))}
    </div>
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader 
        title="Overview" 
        subtitle="Revenue recovery operations"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {loading || openCurrencies.length > 0 ? (
          <MetricCard 
            label="Open Revenue at Risk" 
            value={loading ? <div className="h-9 w-24 bg-[var(--color-surface-secondary)] rounded animate-pulse" /> : revenueDisplay}
          />
        ) : (
          <UnavailableMetric label="Open Revenue at Risk" />
        )}

        <MetricCard 
          label="Active Cases" 
          value={loading ? <div className="h-9 w-12 bg-[var(--color-surface-secondary)] rounded animate-pulse" /> : metrics.activeCases}
        />
        
        {loading || recoveredCurrencies.length > 0 ? (
          <MetricCard 
            label="Verified Recovered" 
            value={loading ? <div className="h-9 w-24 bg-[var(--color-surface-secondary)] rounded animate-pulse" /> : recoveredDisplay}
          />
        ) : (
          <UnavailableMetric label="Verified Recovered" />
        )}
        
        <UnavailableMetric label="Recovery Rate" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h3 className="text-base font-bold font-display text-[var(--color-text-primary)] mb-4">Recovery Funnel</h3>
          {analyticsLoading || !analyticsData ? (
             <div className="space-y-4 mt-2">
               {[1, 2, 3].map(i => (
                 <div key={i} className="flex items-center gap-4">
                   <div className="w-24 h-5 bg-[var(--color-surface-secondary)] rounded animate-pulse" />
                   <div className="h-8 bg-[var(--color-surface-secondary)] rounded animate-pulse" style={{ width: `${100 - i * 20}%` }} />
                 </div>
               ))}
             </div>
          ) : (
            analyticsData.funnel && analyticsData.funnel.length > 0 ? (
               <FunnelChart data={analyticsData.funnel} />
            ) : (
               <p className="text-sm text-[var(--color-text-muted)] italic mt-2">No funnel data available.</p>
            )
          )}
        </div>
        
        <div className="flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">
          <h3 className="text-base font-bold font-display text-[var(--color-text-primary)] mb-4">Outcome Distribution</h3>
          {analyticsLoading || !analyticsData ? (
             <div className="space-y-5 mt-2">
               {[1, 2, 3].map(i => (
                 <div key={i} className="space-y-2">
                   <div className="flex justify-between">
                     <div className="w-16 h-4 bg-[var(--color-surface-secondary)] rounded animate-pulse" />
                     <div className="w-12 h-4 bg-[var(--color-surface-secondary)] rounded animate-pulse" />
                   </div>
                   <div className="w-full h-2.5 bg-[var(--color-surface-secondary)] rounded-full animate-pulse" />
                 </div>
               ))}
             </div>
          ) : (
            analyticsData.outcomeDistribution && analyticsData.outcomeDistribution.length > 0 ? (
               <OutcomeDistribution data={analyticsData.outcomeDistribution} />
            ) : (
               <p className="text-sm text-[var(--color-text-muted)] italic mt-2">No outcome data available.</p>
            )
          )}
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)]">Recent Recovery Cases</h2>
        <CaseTable cases={data?.cases.slice(0, 10) || []} loading={loading} />
      </div>
    </div>
  );
}
