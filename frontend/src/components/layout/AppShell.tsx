import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FileStack, 
  CheckSquare, 
  PlayCircle, 
  ShieldCheck, 
  ClipboardList, 
  BarChart3, 
  Building2, 
  Settings, 
  HelpCircle,
  Menu, 
  X,
  Bell,
  Search,
  UserCircle
} from 'lucide-react';


export function Sidebar({ className = '', onNavClick }: { className?: string, onNavClick?: () => void }) {
  const topLinks = [
    { to: '/', icon: LayoutDashboard, label: 'Overview' },
    { to: '/cases', icon: FileStack, label: 'Recovery Cases' },
    { to: '/approvals', icon: CheckSquare, label: 'Approvals' },
    { to: '/execution', icon: PlayCircle, label: 'Execution' },
    { to: '/verification', icon: ShieldCheck, label: 'Verification' },
    { to: '/audit', icon: ClipboardList, label: 'Audit' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  const bottomLinks = [
    { to: '/merchant', icon: Building2, label: 'Merchant Account' },
    { to: '/settings', icon: Settings, label: 'Settings' },
    { to: '/support', icon: HelpCircle, label: 'Support' },
  ];

  return (
    <nav className={`w-64 border-r border-[var(--color-border)] bg-[var(--color-bg)] h-screen flex flex-col justify-between ${className}`}>
      <div>
        <div className="p-6 pb-2">
          <div className="flex flex-col mb-6">
            <span className="font-display font-bold text-xl tracking-wide text-[var(--color-text-primary)]">RECOVERAI</span>
            <span className="text-[10px] font-mono tracking-widest text-[var(--color-text-secondary)] mt-1">DEMO / TEST MODE</span>
          </div>
        </div>
        <ul className="space-y-0.5 px-3">
          {topLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                onClick={onNavClick}
                end={link.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded transition-colors focus-visible:outline-none ${
                    isActive
                      ? 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] border-l-2 border-[var(--color-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] border-l-2 border-transparent'
                  }`
                }
              >
                <link.icon className="w-4 h-4 opacity-70" />
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="p-3 mb-2">
        <ul className="space-y-0.5">
          {bottomLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                onClick={onNavClick}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded transition-colors focus-visible:outline-none ${
                    isActive
                      ? 'bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] border-l-2 border-[var(--color-primary)]'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] hover:text-[var(--color-text-primary)] border-l-2 border-transparent'
                  }`
                }
              >
                <link.icon className="w-4 h-4 opacity-70" />
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
    <header className="h-16 border-b border-[var(--color-border)] bg-[var(--color-surface)] flex items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-4 lg:hidden">
        <button aria-label="Open menu" onClick={onMenuClick} className="p-2 -ml-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] rounded-lg">
          <Menu className="w-5 h-5" />
        </button>
        <span className="font-display font-bold tracking-tight text-[var(--color-text-primary)]">RECOVERAI</span>
      </div>
      
      <div className="hidden lg:flex items-center bg-[var(--color-bg)] rounded px-3 py-1.5 border border-[var(--color-border)] w-96">
        <Search className="w-4 h-4 text-[var(--color-text-secondary)] mr-2" />
        <input 
          type="text" 
          placeholder="Search cases, IDs..." 
          className="bg-transparent border-none outline-none text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] w-full"
        />
      </div>
      
      <div className="flex items-center gap-4 ml-auto text-[var(--color-text-secondary)]">
        <button className="hover:text-[var(--color-text-primary)] transition-colors">
          <Bell className="w-5 h-5" />
        </button>
        <button className="hover:text-[var(--color-text-primary)] transition-colors">
          <UserCircle className="w-6 h-6" />
        </button>
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

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-bg)]">
      <Sidebar className="hidden lg:flex" />
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-64 bg-[var(--color-bg)] shadow-xl transform transition-transform duration-200">
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="absolute top-4 right-4 p-2 text-[var(--color-text-secondary)]"
            >
              <X className="w-5 h-5" />
            </button>
            <Sidebar onNavClick={() => setMobileMenuOpen(false)} />
          </div>
        </div>
      )}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[var(--color-bg)]">
        <TopBar onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <div className="max-w-[1200px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
