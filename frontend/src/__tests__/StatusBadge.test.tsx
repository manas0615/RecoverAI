import { render, screen } from '@testing-library/react';
import { StatusBadge } from '../components/status/StatusBadge';
import { describe, it, expect } from 'vitest';

describe('StatusBadge', () => {
  it('renders OPEN status correctly', () => {
    render(<StatusBadge status="OPEN" />);
    expect(screen.getByText('OPEN')).toBeInTheDocument();
  });

  it('replaces underscores with spaces', () => {
    render(<StatusBadge status="VERIFIED_SUCCESS" />);
    expect(screen.getByText('VERIFIED SUCCESS')).toBeInTheDocument();
  });
});
