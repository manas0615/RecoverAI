import re

with open('frontend/src/pages/AnalyticsPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Recovery rate block
old_rec = """<div className="text-3xl font-mono text-[var(--color-primary)] font-bold mt-2">{recovery_rate}%</div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Verified recoveries / eligible cases</p>
          <div className="h-1 bg-[var(--color-primary)]/20 mt-4 rounded-full overflow-hidden">
            <div className="h-full bg-[var(--color-primary)]" style={{ width: `${recovery_rate}%` }} />
          </div>"""
new_rec = """<div className="text-3xl font-mono text-[var(--color-primary)] font-bold mt-2">
              {recovery_rate !== null ? `${recovery_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No eligible cases</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Verified recoveries / eligible cases</p>
          {recovery_rate !== null && (
            <div className="h-1 bg-[var(--color-primary)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-primary)]" style={{ width: `${recovery_rate}%` }} />
            </div>
          )}"""
content = content.replace(old_rec, new_rec)

# 2. Verification rate block
old_ver = """<div className="text-3xl font-mono text-[var(--color-success)] font-bold mt-2">{verification_rate}%</div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Provider outcomes independently confirmed</p>
          <div className="h-1 bg-[var(--color-success)]/20 mt-4 rounded-full overflow-hidden">
            <div className="h-full bg-[var(--color-success)]" style={{ width: `${verification_rate}%` }} />
          </div>"""
new_ver = """<div className="text-3xl font-mono text-[var(--color-success)] font-bold mt-2">
              {verification_rate !== null ? `${verification_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No verification outcomes</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Provider outcomes independently confirmed</p>
          {verification_rate !== null && (
            <div className="h-1 bg-[var(--color-success)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-success)]" style={{ width: `${verification_rate}%` }} />
            </div>
          )}"""
content = content.replace(old_ver, new_ver)

# 3. Export button
old_exp = """<button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-primary)] text-white rounded hover:bg-[var(--color-primary)]/90 transition-colors">
            <Download className="w-4 h-4" />
            Export
          </button>"""
new_exp = """<button disabled className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-[var(--color-text-muted)] cursor-not-allowed">
            <Download className="w-4 h-4 opacity-50" />
            Export (Unavailable)
          </button>"""
content = content.replace(old_exp, new_exp)

# 4. trend and gemini
old_det = "const detPct = totalRec > 0 ? Math.round((recommendation_source['Deterministic Fallback'] / totalRec) * 100) : 0;"
new_det = "const detPct = totalRec > 0 ? Math.round((recommendation_source['Deterministic Fallback'] / totalRec) * 100) : 0;\n  const nonZeroBuckets = performance_7d?.filter((d: any) => d.recovered > 0 || d.at_risk > 0).length || 0;\n  const hasMeaningfulTrend = nonZeroBuckets >= 2;"
content = content.replace(old_det, new_det)

# 5. Chart
old_chart = """{performance_7d && performance_7d.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performance_7d} margin={{ top: 5, right: 0, left: 0, bottom: 5 }}>
                  <XAxis dataKey="date" stroke="var(--color-border)" tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }} tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', { weekday: 'short' })} />
                  <YAxis hide domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ fontFamily: 'monospace' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px' }}
                    formatter={(value: any) => formatCurrency(Number(value))}
                    labelFormatter={(label: any) => new Date(label as string).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <Legend iconType="square" wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }} />
                  <Line type="monotone" name="Recovered" dataKey="recovered" stroke="var(--color-primary)" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" name="At Risk" dataKey="at_risk" stroke="var(--color-text-muted)" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-[var(--color-text-muted)]">Insufficient historical data</div>
            )}"""

new_chart = """{hasMeaningfulTrend ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performance_7d} margin={{ top: 5, right: 0, left: 0, bottom: 5 }}>
                  <XAxis dataKey="date" stroke="var(--color-border)" tick={{ fill: 'var(--color-text-muted)', fontSize: 11 }} tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', { weekday: 'short' })} />
                  <YAxis hide domain={['auto', 'auto']} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ fontFamily: 'monospace' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px' }}
                    formatter={(value: any, name: string) => [`₹${(Number(value) / 100).toLocaleString('en-IN')}`, name]}
                    labelFormatter={(label: any) => new Date(label as string).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <Legend iconType="square" wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }} />
                  <Line type="linear" name="Verified Recovered" dataKey="recovered" stroke="var(--color-primary)" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="linear" name="Revenue At Risk" dataKey="at_risk" stroke="var(--color-text-muted)" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-[var(--color-text-muted)]">Insufficient historical data</div>
            )}"""

content = content.replace(old_chart, new_chart)

# 6. P25 Numbers
content = content.replace('54.2%', '52.3%')
content = content.replace('89.2%', '48.5%')

with open('frontend/src/pages/AnalyticsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
