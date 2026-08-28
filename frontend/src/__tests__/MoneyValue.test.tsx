import { render, screen } from '@testing-library/react';
import { MoneyValue } from '../components/financial/MoneyValue';
import { describe, it, expect } from 'vitest';

describe('MoneyValue', () => {
  it('formats INR correctly', () => {
    render(<MoneyValue amountMinor={48250000} currency="INR" />);
    // 48250000 / 100 = 482500
    // "₹4,82,500.00"
    expect(screen.getByText(/4,82,500/)).toBeInTheDocument();
  });

  it('formats USD correctly', () => {
    render(<MoneyValue amountMinor={125000} currency="USD" />);
    // 125000 / 100 = 1250
    // "$1,250.00"
    expect(screen.getByText(/1,250\.00/)).toBeInTheDocument();
  });
});
