
interface MoneyValueProps {
  amountMinor: number;
  currency: string;
  className?: string;
}

export function MoneyValue({ amountMinor, currency, className = '' }: MoneyValueProps) {
  const amount = amountMinor / 100;
  
  const formatted = new Intl.NumberFormat(currency === 'INR' ? 'en-IN' : 'en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);

  return (
    <span className={`font-mono ${className}`}>
      {formatted}
    </span>
  );
}
