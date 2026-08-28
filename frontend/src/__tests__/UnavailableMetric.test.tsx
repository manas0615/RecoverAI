import { render, screen } from '@testing-library/react';
import { UnavailableMetric } from '../components/data-display/UnavailableMetric';
import { describe, it, expect } from 'vitest';

describe('UnavailableMetric', () => {
  it('renders label and unavailable state', () => {
    render(<UnavailableMetric label="Verified Recovered" />);
    expect(screen.getByText('Verified Recovered')).toBeInTheDocument();
    expect(screen.getByText('Data Unavailable')).toBeInTheDocument();
  });
});
