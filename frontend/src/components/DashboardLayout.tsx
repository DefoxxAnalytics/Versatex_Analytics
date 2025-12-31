import { useState, ReactNode } from 'react';
import { Link, useLocation } from 'wouter';
import {
  BarChart3,
  Package,
  Upload,
  FolderTree,
  Users,
  TrendingUp,
  Layers,
  CalendarDays,
  TrendingDown,
  Sparkles,
  LineChart,
  FileText,
  AlertTriangle,
  Settings,
  Menu,
  X,
  SlidersHorizontal,
  LogOut,
  LayoutDashboard,
  Calendar,
  Target,
  Shield,
  User as UserIcon,
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useProcurementData } from '@/hooks/useProcurementData';
import { cn } from '@/lib/utils';
import { Breadcrumb } from './Breadcrumb';
import { FilterPane } from './FilterPane';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';

/**
 * Check if the current user has admin role
 */
function isAdmin(): boolean {
  try {
    const userStr = localStorage.getItem('user');
    if (!userStr) return false;

    const user = JSON.parse(userStr);
    return user?.profile?.role === 'admin';
  } catch {
    return false;
  }
}

/**
 * User information interface
 */
interface UserInfo {
  username: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  role: 'admin' | 'manager' | 'viewer';
  initials: string;
  displayName: string;
}

/**
 * Get current user information from localStorage
 */
function getUserInfo(): UserInfo | null {
  try {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;

    const user = JSON.parse(userStr);
    const firstName = user?.first_name || '';
    const lastName = user?.last_name || '';
    const username = user?.username || 'User';
    const role = user?.profile?.role || 'viewer';

    // Generate initials
    let initials = '';
    if (firstName && lastName) {
      initials = `${firstName[0]}${lastName[0]}`.toUpperCase();
    } else if (firstName) {
      initials = firstName.substring(0, 2).toUpperCase();
    } else if (username) {
      initials = username.substring(0, 2).toUpperCase();
    } else {
      initials = 'U';
    }

    // Generate display name
    let displayName = '';
    if (firstName && lastName) {
      displayName = `${firstName} ${lastName}`;
    } else if (firstName) {
      displayName = firstName;
    } else {
      displayName = username;
    }

    return {
      username,
      firstName,
      lastName,
      email: user?.email,
      role,
      initials,
      displayName,
    };
  } catch {
    return null;
  }
}

/**
 * Navigation item configuration
 * Each item represents a tab in the dashboard
 */
interface NavItem {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

/**
 * Complete navigation configuration for all 13 tabs
 * Organized logically by analysis type
 */
const NAV_ITEMS: NavItem[] = [
  {
    path: '/upload',
    label: 'Upload Data',
    icon: Upload,
    description: 'Upload procurement data files',
  },
  {
    path: '/',
    label: 'Overview',
    icon: LayoutDashboard,
    description: 'Dashboard overview',
  },
  {
    path: '/categories',
    label: 'Categories',
    icon: FolderTree,
    description: 'Spend analysis by category',
  },
  {
    path: '/suppliers',
    label: 'Suppliers',
    icon: Users,
    description: 'Supplier performance and insights',
  },
  {
    path: '/pareto',
    label: 'Pareto Analysis',
    icon: TrendingUp,
    description: '80/20 rule insights',
  },
  {
    path: '/stratification',
    label: 'Spend Stratification',
    icon: Layers,
    description: 'Spend tier analysis',
  },
  {
    path: '/seasonality',
    label: 'Seasonality',
    icon: Calendar,
    description: 'Time-based spending patterns',
  },
  {
    path: '/yoy',
    label: 'Year-over-Year',
    icon: BarChart3,
    description: 'Trend comparison',
  },
  {
    path: '/tail-spend',
    label: 'Tail Spend',
    icon: Target,
    description: 'Long-tail spending analysis',
  },
  {
    path: '/ai-insights',
    label: 'AI Insights',
    icon: Sparkles,
    description: 'Smart recommendations',
  },
  {
    path: '/predictive',
    label: 'Predictive Analytics',
    icon: LineChart,
    description: 'Forecasting and predictions',
  },
  {
    path: '/contracts',
    label: 'Contract Optimization',
    icon: FileText,
    description: 'Contract analysis',
  },
  {
    path: '/maverick',
    label: 'Maverick Spend',
    icon: AlertTriangle,
    description: 'Policy compliance tracking',
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: Settings,
    description: 'Configuration and preferences',
  },
];

/**
 * User display component showing avatar, name, and role
 */
function UserDisplay() {
  const userInfo = getUserInfo();

  if (!userInfo) return null;

  // Role badge styling
  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'admin':
        return 'default'; // Blue
      case 'manager':
        return 'secondary'; // Green-ish
      case 'viewer':
        return 'outline'; // Gray outline
      default:
        return 'outline';
    }
  };

  const getRoleLabel = (role: string) => {
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  return (
    <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-blue-900/50 border border-blue-700">
      {/* Avatar */}
      <Avatar className="h-8 w-8">
        <AvatarFallback className="bg-white text-[#1e3a8a] text-sm font-semibold">
          {userInfo.initials}
        </AvatarFallback>
      </Avatar>

      {/* Name and Role - Hidden on small screens */}
      <div className="hidden md:flex md:flex-col md:gap-0.5">
        <span className="text-sm font-medium text-white leading-tight">
          {userInfo.displayName}
        </span>
        <Badge
          variant={getRoleBadgeVariant(userInfo.role)}
          className="text-xs w-fit"
        >
          {getRoleLabel(userInfo.role)}
        </Badge>
      </div>
    </div>
  );
}

/**
 * Logout button component
 */
function LogoutButton() {
  const { logout } = useAuth();

  return (
    <button
      onClick={logout}
      className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 rounded-md transition-colors"
      title="Logout"
    >
      <LogOut className="h-4 w-4" />
      <span className="hidden sm:inline">Logout</span>
    </button>
  );
}

interface DashboardLayoutProps {
  children?: ReactNode;
}

/**
 * Main dashboard layout component with responsive sidebar navigation
 * 
 * Features:
 * - Responsive design with mobile menu
 * - Active route highlighting
 * - Accessibility support (ARIA labels, keyboard navigation)
 * - Data validation (prompts user to upload if no data)
 * 
 * @param {ReactNode} children - Content to render in the main area
 */
export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [location] = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isFilterPaneOpen, setIsFilterPaneOpen] = useState(true);
  const { data = [] } = useProcurementData();

  /**
   * Check if a navigation item is currently active
   * Handles both exact matches and root path
   */
  const isActive = (path: string): boolean => {
    if (path === '/' && location === '/') return true;
    if (path !== '/' && location.startsWith(path)) return true;
    return false;
  };

  /**
   * Toggle mobile menu state
   * Follows accessibility best practices with ARIA attributes
   */
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen((prev) => !prev);
  };

  /**
   * Close mobile menu when navigation occurs
   * Improves UX on mobile devices
   */
  const handleNavClick = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Navy theme matching admin panel */}
      <header className="bg-[#1e3a8a] border-b border-blue-900 shadow-lg sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/vtx_logo2.png"
              alt="Versatex Logo"
              className="h-10 w-auto brightness-0 invert"
            />
            <h1 className="text-xl font-bold text-white">Analytics Dashboard</h1>
          </div>

          <div className="flex items-center gap-2">
            {/* User Display */}
            <UserDisplay />

            {/* Logout button */}
            <LogoutButton />

            {/* Filter pane toggle */}
            <button
              onClick={() => setIsFilterPaneOpen(!isFilterPaneOpen)}
              className="p-2 rounded-md hover:bg-blue-700 text-white"
              aria-label="Toggle filters"
              aria-expanded={isFilterPaneOpen}
              title="Toggle filter pane"
            >
              <SlidersHorizontal className="h-5 w-5" />
            </button>

            {/* Mobile menu toggle */}
            <button
              onClick={toggleMobileMenu}
              className="lg:hidden p-2 rounded-md hover:bg-blue-700 text-white"
              aria-label="Toggle menu"
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-navigation"
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation - Navy theme */}
        <aside
          id="mobile-navigation"
          className={cn(
            'fixed lg:sticky top-[73px] left-0 h-[calc(100vh-73px)] w-64 bg-[#1e3a8a] border-r border-blue-900',
            'overflow-y-auto transition-transform duration-200 z-30',
            isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          )}
        >
          <nav
            className="p-4 space-y-1"
            aria-label="Main navigation"
          >
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);

              // For Settings, render divider and Admin Panel link before it if user is admin
              if (item.path === '/settings' && isAdmin()) {
                return (
                  <div key="admin-section">
                    {/* Divider with label */}
                    <div className="pt-4 pb-2">
                      <div className="flex items-center gap-2 px-3 mb-3">
                        <Separator className="flex-1 bg-white/20" />
                        <span className="text-xs font-semibold text-white/60 uppercase tracking-wider">
                          Administration
                        </span>
                        <Separator className="flex-1 bg-white/20" />
                      </div>
                    </div>

                    {/* Admin Panel Link */}
                    <a
                      href={`${window.location.protocol}//${window.location.hostname}:8001/admin/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                        'hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50',
                        'text-white/80 hover:text-white'
                      )}
                      title="Django Admin Panel (admins only)"
                    >
                      <Shield className="h-5 w-5 text-white/70" />
                      <span className="text-sm">Admin Panel</span>
                    </a>

                    {/* Settings Link */}
                    <Link
                      href={item.path}
                      onClick={handleNavClick}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                        'hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50',
                        active
                          ? 'bg-white/20 text-white font-medium'
                          : 'text-white/80 hover:text-white'
                      )}
                      aria-current={active ? 'page' : undefined}
                      title={item.description}
                    >
                      <Icon className={cn('h-5 w-5', active ? 'text-white' : 'text-white/70')} />
                      <span className="text-sm">{item.label}</span>
                    </Link>
                  </div>
                );
              }

              // For Settings (non-admin), render divider before it
              if (item.path === '/settings' && !isAdmin()) {
                return (
                  <div key="settings-section">
                    {/* Divider with label */}
                    <div className="pt-4 pb-2">
                      <div className="flex items-center gap-2 px-3 mb-3">
                        <Separator className="flex-1 bg-white/20" />
                        <span className="text-xs font-semibold text-white/60 uppercase tracking-wider">
                          Settings
                        </span>
                        <Separator className="flex-1 bg-white/20" />
                      </div>
                    </div>

                    {/* Settings Link */}
                    <Link
                      href={item.path}
                      onClick={handleNavClick}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                        'hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50',
                        active
                          ? 'bg-white/20 text-white font-medium'
                          : 'text-white/80 hover:text-white'
                      )}
                      aria-current={active ? 'page' : undefined}
                      title={item.description}
                    >
                      <Icon className={cn('h-5 w-5', active ? 'text-white' : 'text-white/70')} />
                      <span className="text-sm">{item.label}</span>
                    </Link>
                  </div>
                );
              }

              return (
                <Link
                  key={item.path}
                  href={item.path}
                  onClick={handleNavClick}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                    'hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white/50',
                    active
                      ? 'bg-white/20 text-white font-medium'
                      : 'text-white/80 hover:text-white'
                  )}
                  aria-current={active ? 'page' : undefined}
                  title={item.description}
                >
                  <Icon className={cn('h-5 w-5', active ? 'text-white' : 'text-white/70')} />
                  <span className="text-sm">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 p-6 lg:p-8">
          {/* Breadcrumb Navigation */}
          <Breadcrumb />
          {/* Show upload prompt if no data */}
          {data.length === 0 && location !== '/' && (
            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>No data uploaded yet.</strong> Please{' '}
                <Link 
                  href="/"
                  className="underline font-medium hover:text-yellow-900"
                >
                  upload your procurement data
                </Link>{' '}
                to view analytics.
              </p>
            </div>
          )}

          {/* Render children or default message */}
          <div className="flex gap-6">
            <div className="flex-1 min-w-0">
              {children || (
                <div className="text-center py-12 text-gray-500">
                  <p>Select a tab from the navigation to view analytics.</p>
                </div>
              )}
            </div>

            {/* Filter Pane */}
            {isFilterPaneOpen && data.length > 0 && (
              <aside className="w-80 flex-shrink-0 hidden lg:block">
                <FilterPane />
              </aside>
            )}
          </div>
        </main>
      </div>

      {/* Mobile menu overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={toggleMobileMenu}
          aria-hidden="true"
        />
      )}
    </div>
  );
}
