import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorState } from '../components/feedback/ErrorState';
import { describe, it, expect, vi } from 'vitest';

describe('ErrorState', () => {
  it('renders message', () => {
    render(<ErrorState message="Test Error" />);
    expect(screen.getByText('Test Error')).toBeInTheDocument();
  });

  it('calls onRetry when clicked', () => {
    const handleRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={handleRetry} />);
    
    fireEvent.click(screen.getByText('Retry'));
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
});
