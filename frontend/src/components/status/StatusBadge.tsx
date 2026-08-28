import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CheckCircle2, AlertTriangle, XCircle, Clock, Ban } from 'lucide-react';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const s = status.toUpperCase();
  
  let colorClass = 'bg-[var(--color-neutral-bg)] text-[var(--color-neutral)]';
  let Icon = null;
  
  // Terminal success
  if (s === 'RECOVERED' || s === 'VERIFIED_SUCCESS') {
    colorClass = 'bg-[var(--color-success-bg)] text-[var(--color-success)] border border-[var(--color-success)]/20';
    Icon = CheckCircle2;
  }
  // Info / In-progress
  else if (s === 'ASSESSED' || s === 'PLANNING' || s === 'POLICY_REVIEW' || s === 'EXECUTING' || s === 'ACTION_EXECUTING') {
    colorClass = 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info)]/20';
    Icon = Clock;
  }
  // Warning / Unknown / Needs attention
  else if (s === 'WAITING_APPROVAL' || s === 'VERIFYING' || s === 'UNKNOWN' || s === 'ESCALATED' || s === 'VERIFICATION_PENDING') {
    colorClass = 'bg-[var(--color-warning-bg)] text-[var(--color-warning)] border border-[var(--color-warning)]/20';
    Icon = AlertTriangle;
  }
  // Failure / Terminal
  else if (s === 'NOT_RECOVERED' || s === 'VERIFIED_FAILURE') {
    colorClass = 'bg-[var(--color-danger-bg)] text-[var(--color-danger)] border border-[var(--color-danger)]/20';
    Icon = XCircle;
  }
  // Suppressed
  else if (s === 'SUPPRESSED') {
    colorClass = 'bg-[var(--color-neutral-bg)] text-[var(--color-neutral)] border border-[var(--color-neutral)]/20';
    Icon = Ban;
  }
  // OPEN/CLOSED basic mapping
  else if (s === 'OPEN') {
    colorClass = 'bg-[var(--color-info-bg)] text-[var(--color-info)] border border-[var(--color-info)]/20';
  } else if (s === 'CLOSED') {
    colorClass = 'bg-[var(--color-neutral-bg)] text-[var(--color-neutral)] border border-[var(--color-neutral)]/20';
  }

  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium', colorClass, className)}>
      {Icon && <Icon className="w-3.5 h-3.5" />}
      {status.replace(/_/g, ' ')}
    </span>
  );
}
