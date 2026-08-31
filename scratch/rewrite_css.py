import os
import json

css = '''@import "tailwindcss";

@theme {
  --color-bg: #111418;
  --color-surface: #1E232B;
  --color-surface-secondary: #272D36;
  --color-border: #333A45;
  --color-border-subtle: #2A303A;

  --color-text-primary: #FFFFFF;
  --color-text-secondary: #A8B3BF;
  --color-text-muted: #74808C;

  --color-success: #35C98B;
  --color-success-bg: rgba(53, 201, 139, 0.1);
  --color-warning: #F2B84B;
  --color-warning-bg: rgba(242, 184, 75, 0.1);
  --color-danger: #F25C5C;
  --color-danger-bg: rgba(242, 92, 92, 0.1);
  --color-info: #7C8CFF;
  --color-info-bg: rgba(124, 140, 255, 0.1);
  --color-neutral: #A8B3BF;
  --color-neutral-bg: rgba(168, 179, 191, 0.1);

  --color-primary: #7C8CFF;
  --color-primary-hover: #6073E6;
  --color-primary-bg: rgba(124, 140, 255, 0.1);

  --font-display: 'Inter', system-ui, sans-serif;
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

body {
  background-color: var(--color-bg);
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.animate-shimmer {
  background: linear-gradient(90deg, var(--color-surface-secondary) 25%, var(--color-border) 50%, var(--color-surface-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite linear;
}
'''
with open('frontend/src/index.css', 'w') as f:
    f.write(css)

print("Wrote CSS")
