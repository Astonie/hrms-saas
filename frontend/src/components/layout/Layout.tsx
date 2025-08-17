import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { 
  Menu, 
  X, 
  Home, 
  Users, 
  Building2, 
  Calendar, 
  DollarSign, 
  TrendingUp, 
  UserPlus, 
  Clock, 
  FileText,
  Settings,
  LogOut,
  Bell,
  Search,
  Sun,
  Moon,
  Network,
  Award,
  Target
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  permissions?: string[];
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { 
    name: 'Employees', 
    href: '/employees', 
    icon: Users
  },
  { 
    name: 'Departments', 
    href: '/departments', 
    icon: Building2
  },
  { 
    name: 'Organization', 
    href: '/organization', 
    icon: Network
  },
  { 
    name: 'Performance', 
    href: '/performance', 
    icon: Award
  },
  { 
    name: 'Leave Management', 
    href: '/leave', 
    icon: Calendar
  },
  { 
    name: 'Payroll', 
    href: '/payroll', 
    icon: DollarSign
  },
  { 
    name: 'Reports', 
    href: '/reports', 
    icon: TrendingUp
  },
  { 
    name: 'Recruitment', 
    href: '/recruitment', 
    icon: UserPlus, 
    permissions: ['recruitment:read'] 
  },
  { 
    name: 'Time Tracking', 
    href: '/attendance', 
    icon: Clock, 
    permissions: ['attendance:read'] 
  },
  { 
    name: 'Documents', 
    href: '/documents', 
    icon: FileText, 
    permissions: ['documents:read'] 
  },
  { 
    name: 'Settings', 
    href: '/settings', 
    icon: Settings, 
    permissions: ['settings:read'] 
  },
];

export default function Layout() {
  // Start with sidebar open on desktop, closed on mobile
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user, logout, hasPermission } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();

  const filteredNavigation = navigation.filter(item => {
    if (!item.permissions) return true;
    return item.permissions.some(permission => hasPermission(permission));
  });

  const handleNavigation = (href: string) => {
    navigate(href);
    setSidebarOpen(false);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="fixed inset-0 bg-gray-600/75 backdrop-blur-sm" />
        </div>
      )}

      {/* Sidebar - Always visible on desktop, toggleable on mobile */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shadow-xl transform transition-all duration-300 ease-in-out lg:relative lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}>
        {/* Sidebar header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/50 dark:bg-gray-800/50">
          <div className="flex items-center">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
              <Building2 className="h-5 w-5 text-white" />
            </div>
            <span className="ml-3 text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              HRMS
            </span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100/80 dark:hover:bg-gray-700/80 transition-all duration-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
          {filteredNavigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={`group flex items-center w-full px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg transform scale-105'
                    : 'text-gray-700 hover:bg-gray-100/80 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700/80 dark:hover:text-white hover:transform hover:scale-105 hover:shadow-sm'
                }`}
              >
                <item.icon
                  className={`mr-4 h-5 w-5 transition-all duration-200 ${
                    isActive
                      ? 'text-white'
                      : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'
                  }`}
                />
                {item.name}
                {isActive && (
                  <div className="ml-auto w-1 h-6 bg-white/30 rounded-full" />
                )}
              </button>
            );
          })}
        </nav>

        {/* User section */}
        <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-gray-50/50 to-gray-100/50 dark:from-gray-800/50 dark:to-gray-900/50">
          <div className="flex items-center p-3 rounded-xl bg-white/80 dark:bg-gray-700/80 shadow-sm">
            <div className="flex-shrink-0">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
                <span className="text-sm font-semibold text-white">
                  {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                </span>
              </div>
            </div>
            <div className="ml-3 min-w-0 flex-1">
              <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                {user?.full_name || user?.username}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.user_type || 'User'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-2 p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top header */}
        <header className="sticky top-0 z-30 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            {/* Left side */}
            <div className="flex items-center flex-1">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100/80 dark:hover:bg-gray-700/80 transition-all duration-200"
              >
                <Menu className="h-6 w-6" />
              </button>
              
              {/* Search */}
              <div className="ml-4 flex-1 max-w-md">
                <label htmlFor="search" className="sr-only">
                  Search
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="search"
                    name="search"
                    className="block w-full pl-12 pr-4 py-3 border-0 rounded-xl bg-gray-50/80 dark:bg-gray-700/80 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:bg-white dark:focus:bg-gray-600 dark:text-white text-sm transition-all duration-200"
                    placeholder="Search anything..."
                    type="search"
                  />
                </div>
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-3">
              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className="p-3 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100/80 dark:hover:bg-gray-700/80 transition-all duration-200"
                title="Toggle theme"
              >
                {theme === 'dark' ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>

              {/* Notifications */}
              <button className="relative p-3 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100/80 dark:hover:bg-gray-700/80 transition-all duration-200">
                <Bell className="h-5 w-5" />
                <span className="absolute top-2 right-2 h-2 w-2 bg-red-500 rounded-full animate-pulse shadow-lg"></span>
              </button>

              {/* User menu */}
              <div className="flex items-center space-x-3 pl-3 border-l border-gray-200 dark:border-gray-700">
                <div className="hidden md:block text-right">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {user?.user_type || 'User'}
                  </p>
                </div>
                <div className="h-10 w-10 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg cursor-pointer hover:scale-105 transition-transform duration-200">
                  <span className="text-sm font-semibold text-white">
                    {user?.first_name?.[0] || user?.username?.[0] || 'U'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-gray-50/50 dark:bg-gray-900/50">
          <div className="p-6 sm:p-8 lg:p-10">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
