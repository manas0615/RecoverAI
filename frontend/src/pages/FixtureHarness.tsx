import { useState } from 'react';
import { CaseDetailView } from './CaseDetailView';
import { fixtures } from '../test-fixtures/cases';
import { PageHeader } from '../components/layout/PageHeader';

export function FixtureHarness() {
  const [selectedFixture, setSelectedFixture] = useState<keyof typeof fixtures>('DETECTED');
  
  return (
    <div className="space-y-8">
      <PageHeader 
        title="UI State Fixtures" 
        subtitle="Development-only isolated UI verification environment."
      />
      
      <div className="flex flex-wrap gap-2 mb-8 p-4 bg-[var(--color-surface-secondary)] rounded-xl border border-[var(--color-border)]">
        {Object.keys(fixtures).map((key) => (
          <button
            key={key}
            onClick={() => setSelectedFixture(key as keyof typeof fixtures)}
            className={`px-3 py-1.5 text-xs font-mono rounded-md transition-colors ${
              selectedFixture === key 
                ? 'bg-[var(--color-primary)] text-white' 
                : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:border-[var(--color-primary)]'
            }`}
          >
            {key}
          </button>
        ))}
      </div>

      <div className="border-t border-[var(--color-border)] pt-8">
        <CaseDetailView 
          caseData={fixtures[selectedFixture].caseData} 
          timeline={fixtures[selectedFixture].timeline} 
        />
      </div>
    </div>
  );
}
