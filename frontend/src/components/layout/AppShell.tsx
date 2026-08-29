import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileStack, Server, Menu, X, ShieldCheck } from 'lucide-react';
import { SystemStatus } from '../status/SystemStatus';
import { TestModeBadge } from '../status/TestModeBadge';

export function Sidebar({ className = '', onNavClick }: { className?: string, onNavClick?: () => void }) {
  const links = [
    { to: '/', icon: LayoutDashboard, label: 'Overview' },
    { to: '/cases', icon: FileStack, label: 'Recovery Cases' },
    { to: '/system', icon: Server, label: 'System Health' },
  ];

  return (
    <nav className={`w-64 border-r border-[var(--color-border)] bg-[var(--color-bg)] h-screen flex flex-col ${className}`}>
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="bg-[var(--color-primary)] text-white p-1.5 rounded-lg">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-[var(--color-text-primary)]">RecoverAI</span>
        </div>
        <ul className="space-y-1">
          {links.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                onClick={onNavClick}
                end={link.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] ${
                    isActive
                      ? 'bg-[var(--color-primary-bg)] text-[var(--color-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)]'
                  }`
                }
              >
                <link.icon className="w-4 h-4" />
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

export function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  return (
    <header className="h-16 border-b border-[var(--color-border)] bg-[var(--color-surface)] flex items-center justify-between px-4 lg:px-8">
      <div className="flex items-center gap-4 lg:hidden">
        <button aria-label="Open menu" onClick={onMenuClick} className="p-2 -ml-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]">
          <Menu className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2">
          <div className="bg-[var(--color-primary)] text-white p-1 rounded-lg">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <span className="font-display font-bold tracking-tight text-[var(--color-text-primary)]">RecoverAI</span>
        </div>
      </div>
      <div className="hidden lg:flex" />
      <div className="flex items-center gap-4 ml-auto">
        <TestModeBadge />
        <SystemStatus />
      </div>
    </header>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileMenuOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg)]">
      {/* Desktop Sidebar */}
      <Sidebar className="hidden lg:flex" />

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 bg-[var(--color-bg)] shadow-xl transform transition-transform duration-200">
            <button
              aria-label="Close menu"
              onClick={() => setMobileMenuOpen(false)}
              className="absolute top-4 right-4 p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]"
            >
              <X className="w-5 h-5" />
            </button>
            <Sidebar onNavClick={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-10">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
