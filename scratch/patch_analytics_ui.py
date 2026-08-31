import re

with open('frontend/src/pages/AnalyticsPage.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. KPI 1: Recovery Rate
content = re.sub(
    r'<div className="text-3xl font-mono text-\[var\(--color-primary\)\] font-bold mt-2">\{recovery_rate\}%</div>\s*</div>\s*<p className="text-xs text-\[var\(--color-text-muted\)\] mt-4">Verified recoveries / eligible cases</p>\s*<div className="h-1 bg-\[var\(--color-primary\)\]/20 mt-4 rounded-full overflow-hidden">\s*<div className="h-full bg-\[var\(--color-primary\)\]" style=\{\{ width: `\$\{recovery_rate\}%` \}\} />\s*</div>',
    r"""<div className="text-3xl font-mono text-[var(--color-primary)] font-bold mt-2">
              {recovery_rate !== null ? `${recovery_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No eligible cases</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Verified recoveries / eligible cases</p>
          {recovery_rate !== null && (
            <div className="h-1 bg-[var(--color-primary)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-primary)]" style={{ width: `${recovery_rate}%` }} />
            </div>
          )}""",
    content
)

# 2. KPI 2: Verification Rate
content = re.sub(
    r'<div className="text-3xl font-mono text-\[var\(--color-success\)\] font-bold mt-2">\{verification_rate\}%</div>\s*</div>\s*<p className="text-xs text-\[var\(--color-text-muted\)\] mt-4">Provider outcomes independently confirmed</p>\s*<div className="h-1 bg-\[var\(--color-success\)\]/20 mt-4 rounded-full overflow-hidden">\s*<div className="h-full bg-\[var\(--color-success\)\]" style=\{\{ width: `\$\{verification_rate\}%` \}\} />\s*</div>',
    r"""<div className="text-3xl font-mono text-[var(--color-success)] font-bold mt-2">
              {verification_rate !== null ? `${verification_rate}%` : <span className="text-lg text-[var(--color-text-muted)]">—<br/><span className="text-sm">No verification outcomes</span></span>}
            </div>
          </div>
          <p className="text-xs text-[var(--color-text-muted)] mt-4">Provider outcomes independently confirmed</p>
          {verification_rate !== null && (
            <div className="h-1 bg-[var(--color-success)]/20 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[var(--color-success)]" style={{ width: `${verification_rate}%` }} />
            </div>
          )}""",
    content
)

# 3. Export button
content = re.sub(
    r'<button className="flex items-center gap-2 px-3 py-1\.5 text-sm font-medium bg-\[var\(--color-primary\)\] text-white rounded hover:bg-\[var\(--color-primary\)\]/90 transition-colors">\s*<Download className="w-4 h-4" />\s*Export\s*</button>',
    r"""<button disabled className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded text-[var(--color-text-muted)] cursor-not-allowed">
            <Download className="w-4 h-4 opacity-50" />
            Export (Unavailable)
          </button>""",
    content
)

# 4. Chart rendering logic
# Inject hasMeaningfulTrend calculation right before return statement
content = content.replace(
    '  const geminiPct = totalRec > 0 ? Math.round((recommendation_source[\'Gemini\'] / totalRec) * 100) : 0;\n  const detPct = totalRec > 0 ? Math.round((recommendation_source[\'Deterministic Fallback\'] / totalRec) * 100) : 0;',
    '  const geminiPct = totalRec > 0 ? Math.round((recommendation_source[\'Gemini\'] / totalRec) * 100) : 0;\n  const detPct = totalRec > 0 ? Math.round((recommendation_source[\'Deterministic Fallback\'] / totalRec) * 100) : 0;\n\n  const nonZeroBuckets = performance_7d?.filter((d: any) => d.recovered > 0 || d.at_risk > 0).length || 0;\n  const hasMeaningfulTrend = nonZeroBuckets >= 2;'
)

# Replace Chart rendering block
old_chart = r"""\{performance_7d && performance_7d\.length > 0 \? \(\s*<ResponsiveContainer width="100%" height="100%">\s*<LineChart data=\{performance_7d\} margin=\{\{ top: 5, right: 0, left: 0, bottom: 5 \}\}>\s*<XAxis dataKey="date" stroke="var\(--color-border\)" tick=\{\{ fill: 'var\(--color-text-muted\)', fontSize: 11 \}\} tickFormatter=\{\(val\) => new Date\(val\)\.toLocaleDateString\('en-US', \{ weekday: 'short' \}\)\} />\s*<YAxis hide domain=\{\['auto', 'auto'\]\} />\s*<Tooltip\s*contentStyle=\{\{ backgroundColor: 'var\(--color-surface\)', border: '1px solid var\(--color-border\)', borderRadius: '8px' \}\}\s*itemStyle=\{\{ fontFamily: 'monospace' \}\}\s*labelStyle=\{\{ color: 'var\(--color-text-secondary\)', marginBottom: '4px' \}\}\s*formatter=\{\(value: any\) => formatCurrency\(Number\(value\)\)\}\s*labelFormatter=\{\(label: any\) => new Date\(label as string\)\.toLocaleDateString\('en-US', \{ month: 'short', day: 'numeric' \}\)\}\s*/>\s*<Legend iconType="square" wrapperStyle=\{\{ fontSize: '12px', color: 'var\(--color-text-secondary\)' \}\} />\s*<Line type="monotone" name="Recovered" dataKey="recovered" stroke="var\(--color-primary\)" strokeWidth=\{3\} dot=\{false\} activeDot=\{\{ r: 6 \}\} />\s*<Line type="monotone" name="At Risk" dataKey="at_risk" stroke="var\(--color-text-muted\)" strokeWidth=\{2\} strokeDasharray="5 5" dot=\{false\} />\s*</LineChart>\s*</ResponsiveContainer>\s*\) : \(\s*<div className="h-full flex items-center justify-center text-sm text-\[var\(--color-text-muted\)\]">Insufficient historical data</div>\s*\)"""

new_chart = r"""{hasMeaningfulTrend ? (
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

content = re.sub(old_chart, new_chart, content)

# 5. P25 Numbers - replace 54.2% -> 52.3% and 89.2% -> 48.5%
content = content.replace('54.2%', '52.3%')
content = content.replace('89.2%', '48.5%')

with open('frontend/src/pages/AnalyticsPage.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
