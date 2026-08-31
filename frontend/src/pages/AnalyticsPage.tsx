import { useState } from 'react';
import { useAnalytics } from '../hooks/useApi';
import { RefreshCw, Filter, Download, Info, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';
import { MoneyValue } from '../components/financial/MoneyValue';
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

export function AnalyticsPage() {
  const { data, loading, error, refetch } = useAnalytics();
  const [period, setPeriod] = useState('7D');

  if (error) {
    return (
      <div className="p-8 text-center text-[var(--color-danger)] flex flex-col items-center justify-center min-h-[50vh]">
        <AlertTriangle className="w-12 h-12 mb-4 opacity-50" />
        <h2 className="text-xl font-display font-bold">Unable to load analytics.</h2>
        <p className="text-sm mt-2 opacity-80">{error.message}</p>
        <button onClick={refetch} className="mt-6 px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-border)] transition-colors">
          Retry
        </button>
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="h-10 w-1/4 bg-[var(--color-surface)] rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="h-32 bg-[var(--color-surface)] rounded-xl"></div>
          <div className="h-32 bg-[var(--color-surface)] rounded-xl"></div>
          <div className="h-32 bg-[var(--color-surface)] rounded-xl"></div>
          <div className="h-32 bg-[var(--color-surface)] rounded-xl"></div>
        </div>
      </div>
    );
  }

  // Formatting helpers
  
  // Destructure backend data
  const {
    recovery_rate,
    verification_rate,
    revenue_at_risk,
    verified_recovered,
    performance_7d,
    recovery_outcomes,
    intervention_performance,
    recommendation_source,
    lifecycle,
    failure_causes,
    verification_outcomes
  } = data;

  const totalRec = (recommendation_source?.['Gemini'] || 0) + (recommendation_source?.['Deterministic Fallback'] || 0);
  const geminiPct = totalRec > 0 ? Math.round((recommendation_source['Gemini'] / totalRec) * 100) : 0;
  const detPct = totalRec > 0 ? Math.round((recommendation_source['Deterministic Fallback'] / totalRec) * 100) : 0;

  const nonZeroBuckets = performance_7d?.filter((d: any) => d.recovered > 0 || d.at_risk > 0).length || 0;
  const hasMeaningfulTrend = nonZeroBuckets >= 2;

  return (
    <div className="max-w-[1440px] mx-auto p-4 md:p-8 animate-in fade-in duration-300">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold font-display text-[var(--color-text-primary)] tracking-tight">Analytics</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">Measure recovery effectiveness, intervention outcomes, and operational performance.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={refetch} className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-border-subtle)] transition-colors">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded hover:bg-[var(--color-border-subtle)] transition-colors">
            <Filter className="w-4 h-4" />
            Filters
          </button>
          <button disabled className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-[var(--color-text-muted)] cursor-not-allowed">
            <Download className="w-4 h-4 opacity-50" />
            Export (Unavailable)
          </button>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold font-display uppercase tracking-wider text-[var(--color-text-secondary)]">RECOVERY RATE</h3>
            <div className="text-3xl font-mono text-[var(--color-primary)] font-bold mt-2">
              {recovery_rate !== null ? `${recovery_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No eligible cases</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Verified recoveries / eligible cases</p>
          {recovery_rate !== null && (
            <div className="h-1 bg-[var(--color-primary)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-primary)]" style={{ width: `${recovery_rate}%` }} />
            </div>
          )}
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold font-display uppercase tracking-wider text-[var(--color-text-secondary)]">REVENUE RECOVERED</h3>
            <div className="text-3xl font-mono text-[var(--color-success)] font-bold mt-2">
              <MoneyValue amountMinor={verified_recovered.INR || 0} currency="INR" />
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Verified recovery outcomes</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold font-display uppercase tracking-wider text-[var(--color-text-secondary)]">REVENUE AT RISK</h3>
            <div className="text-3xl font-mono text-[var(--color-warning)] font-bold mt-2">
              <MoneyValue amountMinor={revenue_at_risk.INR || 0} currency="INR" />
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Currently unresolved exposure</p>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold font-display uppercase tracking-wider text-[var(--color-text-secondary)]">VERIFICATION RATE</h3>
            <div className="text-3xl font-mono text-[var(--color-success)] font-bold mt-2">
              {verification_rate !== null ? `${verification_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No verification outcomes</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Provider outcomes independently confirmed</p>
          {verification_rate !== null && (
            <div className="h-1 bg-[var(--color-success)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-success)]" style={{ width: `${verification_rate}%` }} />
            </div>
          )}
        </div>
      </div>

      {/* Row 2: Charts & Outcomes */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)]">Recovery Performance</h2>
              <p className="text-xs text-[var(--color-text-secondary)]">Recovery outcomes over the selected period</p>
            </div>
            <div className="flex bg-[var(--color-bg-primary)] p-1 rounded-lg border border-[var(--color-border)]">
              {['7D', '30D', '90D'].map(p => (
                <button 
                  key={p} 
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 text-xs font-medium rounded ${period === p ? 'bg-[var(--color-surface)] text-[var(--color-text-primary)] shadow-sm' : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'}`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
          <div className="h-[250px] w-full">
            {hasMeaningfulTrend ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performance_7d} margin={{ top: 5, right: 0, left: 0, bottom: 5 }}>
                  <XAxis dataKey="date" stroke="var(--color-border)" tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }} tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', { weekday: 'short' })} />
                  <YAxis hide domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ fontFamily: 'monospace' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px' }}
                    formatter={(value: any, name: any) => [`₹${(Number(value) / 100).toLocaleString('en-IN')}`, name]}
                    labelFormatter={(label: any) => new Date(label as string).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <Legend iconType="square" wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }} />
                  <Line type="linear" name="Verified Recovered" dataKey="recovered" stroke="var(--color-primary)" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="linear" name="Revenue At Risk" dataKey="at_risk" stroke="var(--color-text-muted)" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-[var(--color-text-muted)]">Insufficient historical data</div>
            )}
          </div>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 flex flex-col">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Outcomes</h2>
          <div className="flex-1 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-success)]" /> <span className="text-[var(--color-text-secondary)]">Recovered</span></div>
                <span className="font-mono text-[var(--color-success)]">{recovery_outcomes?.RECOVERED || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-primary)]" /> <span className="text-[var(--color-text-secondary)]">Executing</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{recovery_outcomes?.EXECUTING || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-warning)]" /> <span className="text-[var(--color-text-secondary)]">Awaiting Approval</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{recovery_outcomes?.AWAITING_APPROVAL || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-danger)] opacity-80" /> <span className="text-[var(--color-text-secondary)]">Escalated</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{recovery_outcomes?.ESCALATED || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-text-muted)]" /> <span className="text-[var(--color-text-secondary)]">Unrecoverable</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{recovery_outcomes?.UNRECOVERABLE || 0}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-border)]" /> <span className="text-[var(--color-text-secondary)]">Verif. Pending</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{recovery_outcomes?.VERIF_PENDING || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Strategy & Provenance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 overflow-x-auto">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Intervention Performance</h2>
          <table className="w-full text-left border-collapse min-w-[600px]">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-xs font-bold font-display uppercase tracking-wider text-[var(--color-text-secondary)]">
                <th className="pb-3">Strategy</th>
                <th className="pb-3 text-right">Cases</th>
                <th className="pb-3 text-right">Recovered</th>
                <th className="pb-3 text-right">Failed</th>
                <th className="pb-3 text-right">Pending</th>
                <th className="pb-3 text-right">Recovery Rate</th>
              </tr>
            </thead>
            <tbody>
              {intervention_performance?.map((perf: any, idx: number) => (
                <tr key={idx} className="border-b border-[var(--color-border-subtle)] last:border-0">
                  <td className="py-3 font-mono text-xs text-[var(--color-text-primary)]">{perf.strategy}</td>
                  <td className="py-3 text-right font-mono text-sm text-[var(--color-text-secondary)]">{perf.cases}</td>
                  <td className="py-3 text-right font-mono text-sm text-[var(--color-success)]">{perf.recovered}</td>
                  <td className="py-3 text-right font-mono text-sm text-[var(--color-text-muted)]">{perf.failed}</td>
                  <td className="py-3 text-right font-mono text-sm text-[var(--color-text-secondary)]">{perf.pending}</td>
                  <td className="py-3 text-right font-mono text-sm text-[var(--color-text-primary)]">{perf.recovery_rate}%</td>
                </tr>
              ))}
              {(!intervention_performance || intervention_performance.length === 0) && (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-sm text-[var(--color-text-muted)]">No operational strategies recorded</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recommendation Source</h2>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center text-sm mb-2">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-primary)]" /> <span className="text-[var(--color-text-secondary)]">Gemini</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{geminiPct}%</span>
              </div>
              <div className="flex justify-between items-center text-sm mb-4">
                <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-[var(--color-border)]" /> <span className="text-[var(--color-text-secondary)]">Deterministic Fallback</span></div>
                <span className="font-mono text-[var(--color-text-primary)]">{detPct}%</span>
              </div>
              <div className="h-2 w-full flex rounded-full overflow-hidden">
                <div className="h-full bg-[var(--color-primary)]" style={{ width: `${geminiPct}%` }} />
                <div className="h-full bg-[var(--color-border)]" style={{ width: `${detPct}%` }} />
              </div>
            </div>
            <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
              AI models primarily drove successful interventions, with deterministic fallback handling edge cases.
            </p>
          </div>
        </div>
      </div>

      {/* Row 4: Lifecycle */}
      <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6 mb-8 overflow-x-auto">
        <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Recovery Lifecycle</h2>
        <div className="flex justify-between items-center min-w-[800px] px-4 pb-2">
          {lifecycle?.map((stage: any, idx: number) => {
            const isLast = idx === lifecycle.length - 1;
            const isApproval = stage.stage === 'HUMAN_APPROVAL';
            const isExecuting = stage.stage === 'EXECUTING';
            const isVerified = stage.stage === 'VERIFIED';
            
            let color = 'var(--color-border)';
            if (isVerified) color = 'var(--color-success)';
            else if (isApproval) color = 'var(--color-warning)';
            else if (isExecuting) color = 'var(--color-primary)';
            
            return (
              <div key={idx} className="flex flex-col items-center flex-1 relative">
                {!isLast && <div className="absolute top-6 left-[50%] w-full h-[2px] bg-[var(--color-border-subtle)] -z-10"></div>}
                <div className="w-12 h-12 rounded-full bg-[var(--color-bg-primary)] border-2 flex items-center justify-center font-mono text-sm z-10" style={{ borderColor: color, color }}>
                  {stage.count}
                </div>
                <span className="text-xs font-medium text-[var(--color-text-secondary)] mt-3 capitalize">{stage.stage.replace('_', ' ').toLowerCase()}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Row 5: Failures & Verifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Failure Causes</h2>
          <div className="space-y-4">
            {failure_causes?.map((cause: any, idx: number) => {
              const maxCount = Math.max(...failure_causes.map((c: any) => c.count), 1);
              const pct = (cause.count / maxCount) * 100;
              return (
                <div key={idx} className="flex items-center gap-4 text-sm">
                  <span className="w-32 text-[var(--color-text-secondary)] truncate" title={cause.cause}>{cause.cause}</span>
                  <div className="flex-1 h-1.5 bg-[var(--color-bg-primary)] rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--color-text-muted)]" style={{ width: `${pct}%` }}></div>
                  </div>
                  <span className="w-6 text-right font-mono text-[var(--color-text-primary)]">{cause.count}</span>
                </div>
              );
            })}
            {(!failure_causes || failure_causes.length === 0) && (
              <div className="text-sm text-[var(--color-text-muted)] text-center py-4">No failure records available</div>
            )}
          </div>
        </div>

        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-6">
          <h2 className="text-lg font-bold font-display text-[var(--color-text-primary)] mb-6">Verification Outcomes</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 rounded bg-[var(--color-bg-primary)] border border-[var(--color-border-subtle)]">
              <span className="text-sm text-[var(--color-text-secondary)]">Provider Matched</span>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[var(--color-success)]/10 text-[var(--color-success)]">SUCCESS</span>
                <span className="font-mono text-sm text-[var(--color-text-primary)]">{verification_outcomes?.['Provider Matched'] || 0}</span>
              </div>
            </div>
            <div className="flex justify-between items-center p-3 rounded bg-[var(--color-bg-primary)] border border-[var(--color-border-subtle)]">
              <span className="text-sm text-[var(--color-text-secondary)]">Mismatch Detected</span>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[var(--color-danger)]/10 text-[var(--color-danger)]">MISMATCH</span>
                <span className="font-mono text-sm text-[var(--color-text-primary)]">{verification_outcomes?.['Mismatch Detected'] || 0}</span>
              </div>
            </div>
            <div className="flex justify-between items-center p-3 rounded bg-[var(--color-bg-primary)] border border-[var(--color-border-subtle)]">
              <span className="text-sm text-[var(--color-text-secondary)]">Verification Pending</span>
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[var(--color-warning)]/10 text-[var(--color-warning)]">UNKNOWN</span>
                <span className="font-mono text-sm text-[var(--color-text-primary)]">{verification_outcomes?.['Verification Pending'] || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 6: Insight Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 flex flex-col justify-between opacity-80">
          <div className="flex items-center gap-2 text-[var(--color-primary)] mb-2">
            <Info className="w-4 h-4" />
            <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Time to Recover</h3>
          </div>
          <p className="text-xs text-[var(--color-text-muted)]">Not enough data to calculate operational average.</p>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 flex flex-col justify-between opacity-80">
          <div className="flex items-center gap-2 text-[var(--color-warning)] mb-2">
            <AlertTriangle className="w-4 h-4" />
            <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Approval Bottleneck</h3>
          </div>
          <p className="text-xs text-[var(--color-text-muted)]">Not enough data to calculate queue latency.</p>
        </div>
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 flex flex-col justify-between opacity-80">
          <div className="flex items-center gap-2 text-[var(--color-success)] mb-2">
            <Activity className="w-4 h-4" />
            <h3 className="text-sm font-bold text-[var(--color-text-primary)]">Link Conversion</h3>
          </div>
          <p className="text-xs text-[var(--color-text-muted)]">Metric unavailable for current period.</p>
        </div>
      </div>

      {/* Row 7: P25 Benchmark */}
      <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border-subtle)] rounded-xl p-6 mb-8 mt-12 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-[var(--color-text-muted)]"></div>
        <div className="mb-4">
          <span className="text-[10px] font-bold font-mono bg-[var(--color-surface)] text-[var(--color-text-muted)] px-2 py-1 rounded border border-[var(--color-border)]">P25</span>
          <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] ml-3">SYNTHETIC QUANTITATIVE BENCHMARK</span>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div>
            <h3 className="text-sm font-bold text-[var(--color-text-primary)] mb-1">Performance vs Baseline</h3>
            <p className="text-xs text-[var(--color-text-muted)]">Recovery Rate (Case) comparison against standard deterministic rule-based recovery.</p>
          </div>
          
          <div className="flex items-center gap-6 bg-[var(--color-surface)] px-6 py-4 rounded border border-[var(--color-border-subtle)]">
            <div className="text-right">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-muted)] mb-1">SIMPLE RULE</div>
              <div className="text-xl font-mono text-[var(--color-text-secondary)]">52.3%</div>
            </div>
            <div className="text-[var(--color-text-muted)] font-mono">→</div>
            <div className="text-right">
              <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--color-primary)] mb-1">RECOVERAI</div>
              <div className="text-xl font-mono text-[var(--color-success)]">48.5%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Banner */}
      <div className="flex items-center justify-center gap-2 py-4 bg-[var(--color-surface)] border border-[var(--color-border-subtle)] rounded text-xs text-[var(--color-text-secondary)]">
        <ShieldCheck className="w-4 h-4 text-[var(--color-text-muted)]" />
        <strong>Analytics Boundary:</strong> Metrics reflect independently verified outcomes recorded in the operational ledger.
      </div>
      
    </div>
  );
}
