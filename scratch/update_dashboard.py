import os
import re

# 1. Update RecoveryJourney.tsx to be the vertical component
recovery_journey = """import { Check, AlertTriangle, X } from 'lucide-react';

interface RecoveryJourneyProps {
  currentState: string;
}

const STAGES = [
  { id: 'DETECTED', label: 'Evidence Collected', states: ['DETECTED'] },
  { id: 'ASSESSED', label: 'Recommendation', states: ['ENRICHING', 'ASSESSED'] },
  { id: 'POLICY', label: 'Policy Check', states: ['PLANNING', 'POLICY_REVIEW'] },
  { id: 'APPROVAL', label: 'Human Approval', states: ['WAITING_APPROVAL', 'ESCALATED'] },
  { id: 'EXECUTING', label: 'Execution', states: ['EXECUTING', 'ACTION_EXECUTING', 'UNKNOWN', 'ACTION_EXECUTION_UNKNOWN'] },
  { id: 'VERIFYING', label: 'Verification', states: ['VERIFYING', 'VERIFICATION_STARTED', 'VERIFICATION_PENDING', 'VERIFIED_SUCCESS', 'VERIFIED_FAILURE', 'RECOVERED', 'CLOSED'] },
];

export function RecoveryJourney({ currentState }: RecoveryJourneyProps) {
  const isFailed = ['VERIFIED_FAILURE', 'NOT_RECOVERED', 'SUPPRESSED'].includes(currentState);
  const isUnknown = currentState === 'UNKNOWN';
  const isSuccess = ['VERIFIED_SUCCESS', 'RECOVERED', 'CLOSED'].includes(currentState) && !isFailed && !isUnknown;
  const isEscalated = currentState === 'ESCALATED';
  const isWaitingApproval = currentState === 'WAITING_APPROVAL';
  const isApprovalStage = isEscalated || isWaitingApproval;

  let activeIndex = STAGES.findIndex(s => s.states.includes(currentState));
  if (activeIndex === -1 && (isSuccess || isFailed)) {
    activeIndex = STAGES.length - 1;
  }
  if (activeIndex === -1) activeIndex = 0; // Default fallback

  return (
    <div className="flex flex-col space-y-0 w-full relative">
      {/* Global vertical connector line */}
      <div className="absolute top-4 bottom-4 left-[11px] w-[2px] bg-[var(--color-border-subtle)]" />
      
      {STAGES.map((stage, index) => {
        const isCompleted = index < activeIndex || (index === activeIndex && isSuccess);
        const isActive = index === activeIndex && !isSuccess;
        
        let circleClass = 'bg-[var(--color-surface)] border-[var(--color-border)] text-[var(--color-text-muted)]';
        let Icon = () => <span className="w-2 h-2 rounded-full bg-current" />;
        let textClass = 'text-[var(--color-text-secondary)]';
        let subtext = '';

        if (isCompleted) {
          circleClass = 'bg-[var(--color-success)] border-[var(--color-success)] text-white';
          textClass = 'text-[var(--color-text-primary)]';
          Icon = () => <Check className="w-3 h-3" />;
        } else if (isActive) {
          if (isFailed) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-danger)] text-[var(--color-danger)]';
            textClass = 'text-[var(--color-danger)]';
            Icon = () => <X className="w-3 h-3" />;
          } else if (isApprovalStage) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-warning)] text-[var(--color-warning)]';
            textClass = 'text-[var(--color-warning)]';
            subtext = 'Waiting on operator action';
            Icon = () => <AlertTriangle className="w-3 h-3" />;
          } else if (isUnknown) {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-warning)] text-[var(--color-warning)]';
            textClass = 'text-[var(--color-warning)]';
            Icon = () => <AlertTriangle className="w-3 h-3" />;
          } else {
            circleClass = 'bg-[var(--color-surface)] border-[var(--color-primary)] text-[var(--color-primary)]';
            textClass = 'text-[var(--color-primary)]';
          }
        }
        
        return (
          <div key={stage.id} className="relative flex items-start group min-h-[3rem]">
            {/* Step indicator column */}
            <div className="relative z-10 flex items-center justify-center w-6 h-6 mt-0.5 rounded-full border-2 bg-[var(--color-surface)] shrink-0 mr-4 transition-colors duration-300 " + circleClass}>
              <Icon />
            </div>
            
            {/* Content column */}
            <div className="flex-1 pb-4">
              <h4 className={"text-sm font-medium transition-colors " + textClass}>
                {stage.label}
              </h4>
              {subtext && (
                <div className="text-xs text-[var(--color-text-secondary)] mt-1 whitespace-normal">
                  {subtext}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
"""
with open('frontend/src/components/financial/RecoveryJourney.tsx', 'w', encoding='utf-8') as f:
    f.write(recovery_journey)

# 2. Update Dashboard.tsx
with open('frontend/src/pages/Dashboard.tsx', 'r', encoding='utf-8') as f:
    dash = f.read()

# Add imports for Link and Recharts
if "import { Link } from 'react-router-dom';" not in dash:
    dash = dash.replace("import { useAnalytics", "import { Link } from 'react-router-dom';\nimport { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid } from 'recharts';\nimport { useAnalytics")

if "import { RecoveryJourney } from '../components/financial/RecoveryJourney';" not in dash:
    dash = dash.replace("import { AlertTriangle", "import { RecoveryJourney } from '../components/financial/RecoveryJourney';\nimport { AlertTriangle")

# Replace priority case card with Link wrapper
old_priority_start = '<div className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm">'
new_priority_start = '<Link to={`/cases/${pd.id}`} className="lg:col-span-2 flex flex-col p-6 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-sm hover:border-[var(--color-primary)] hover:bg-[var(--color-surface-secondary)] transition-all cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">'
dash = dash.replace(old_priority_start, new_priority_start)

# The end of the priority card needs to close the Link instead of div.
# But it's tricky to regex. The priority card is the lg:col-span-2 div.
# I'll just find the specific pattern if possible, or use simple string manipulation.
# Let's find the closing tag for the priority case.
# It ends with:
#             <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">No priority cases require attention.</div>
#           )}
#         </div>
old_priority_end = """            <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">No priority cases require attention.</div>
          )}
        </div>"""
new_priority_end = """            <div className="flex items-center justify-center h-full text-[var(--color-text-muted)]">No priority cases require attention.</div>
          )}
        </Link>"""
dash = dash.replace(old_priority_end, new_priority_end)

# Also need to stop propagation on the "Approve" button so clicking it doesn't navigate.
approve_button = "onClick={handleApprove}"
new_approve_button = "onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleApprove(); }}"
dash = dash.replace(approve_button, new_approve_button)

# Update Lifecycle panel
lifecycle_old = """            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[var(--color-border)] before:to-transparent">
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
            </div>"""

lifecycle_new = """            {pd ? (
              <RecoveryJourney currentState={pd.workflow_state} />
            ) : (
              <div className="text-sm text-[var(--color-text-muted)]">No active lifecycle.</div>
            )}"""

if lifecycle_old in dash:
    dash = dash.replace(lifecycle_old, lifecycle_new)

# Update chart
chart_old = """          <div className="h-48 flex items-end justify-between px-2 text-[var(--color-text-muted)] text-xs font-mono relative">
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
          </div>"""

chart_new = """          <div className="h-48 w-full text-xs font-mono">
            {!analyticsData ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-[var(--color-text-muted)]">
                 <div className="animate-pulse bg-[var(--color-surface-secondary)] w-full h-full rounded"></div>
              </div>
            ) : !analyticsData.performance_7d || analyticsData.performance_7d.length === 0 ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-[var(--color-text-muted)] text-center">
                 <div>Insufficient historical data</div>
                 <div className="text-[10px] mt-1 opacity-70">Recovery performance will appear as verified outcomes accumulate.</div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analyticsData.performance_7d} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border-subtle)" />
                  <XAxis 
                    dataKey="date" 
                    stroke="var(--color-text-muted)" 
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { weekday: 'short' })}
                  />
                  <YAxis 
                    stroke="var(--color-text-muted)"
                    tick={{ fill: 'var(--color-text-muted)', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => '₹' + (val / 100).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '0.5rem', color: 'var(--color-text-primary)' }}
                    itemStyle={{ color: 'var(--color-text-primary)', fontSize: '12px' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px', fontSize: '12px', fontFamily: 'var(--font-sans)' }}
                    formatter={(val, name) => ['₹' + (Number(val) / 100).toLocaleString(), name === 'recovered' ? 'Verified Recovered' : 'Revenue at Risk']}
                    labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}
                  />
                  <Line type="monotone" dataKey="recovered" stroke="var(--color-primary)" strokeWidth={2} dot={{ r: 3, fill: 'var(--color-surface)', strokeWidth: 2 }} activeDot={{ r: 5, strokeWidth: 0, fill: 'var(--color-primary)' }} />
                  <Line type="monotone" dataKey="at_risk" stroke="var(--color-warning)" strokeWidth={2} strokeDasharray="4 4" dot={false} activeDot={{ r: 4, strokeWidth: 0, fill: 'var(--color-warning)' }} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>"""

if chart_old in dash:
    dash = dash.replace(chart_old, chart_new)
else:
    print("Warning: chart block not found for replacement!")

with open('frontend/src/pages/Dashboard.tsx', 'w', encoding='utf-8') as f:
    f.write(dash)

print("Updated Dashboard and RecoveryJourney")
