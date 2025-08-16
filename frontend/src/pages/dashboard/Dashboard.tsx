import React from 'react';
import { 
  Users, 
  Building2, 
  Calendar, 
  DollarSign, 
  TrendingUp, 
  Clock, 
  UserPlus, 
  FileText,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Plus
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, icon: Icon, color }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
    </div>
    <div className="mt-4 flex items-center">
      {change >= 0 ? (
        <ArrowUpRight className="h-4 w-4 text-green-500" />
      ) : (
        <ArrowDownRight className="h-4 w-4 text-red-500" />
      )}
      <span className={`text-sm font-medium ml-1 ${
        change >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
      }`}>
        {Math.abs(change)}%
      </span>
      <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">from last month</span>
    </div>
  </div>
);

interface QuickActionProps {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  href: string;
  color: string;
}

const QuickAction: React.FC<QuickActionProps> = ({ title, description, icon: Icon, href, color }) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer">
    <div className="flex items-center">
      <div className={`p-3 rounded-lg ${color} mr-4`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <div className="flex-1">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{description}</p>
      </div>
      <ArrowUpRight className="h-5 w-5 text-gray-400" />
    </div>
  </div>
);

interface RecentActivityProps {
  type: string;
  description: string;
  time: string;
  user: string;
}

const RecentActivity: React.FC<RecentActivityProps> = ({ type, description, time, user }) => (
  <div className="flex items-start space-x-3 py-3">
    <div className="flex-shrink-0">
      <div className="h-8 w-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
        <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
          {type.charAt(0).toUpperCase()}
        </span>
      </div>
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-sm text-gray-900 dark:text-white">{description}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
        by {user} • {time}
      </p>
    </div>
  </div>
);

export default function Dashboard() {
  const { user, hasPermission } = useAuth();

  // Mock data - in real app, this would come from API
  const metrics = [
    {
      title: 'Total Employees',
      value: '1,234',
      change: 12,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Departments',
      value: '24',
      change: 5,
      icon: Building2,
      color: 'bg-green-500',
    },
    {
      title: 'Leave Requests',
      value: '89',
      change: -8,
      icon: Calendar,
      color: 'bg-yellow-500',
    },
    {
      title: 'Active Recruitments',
      value: '12',
      change: 25,
      icon: UserPlus,
      color: 'bg-purple-500',
    },
  ];

  const quickActions = [
    {
      title: 'Add Employee',
      description: 'Create a new employee record',
      icon: Plus,
      href: '/employees/new',
      color: 'bg-blue-500',
    },
    {
      title: 'View Leave Calendar',
      description: 'Check leave schedules and approvals',
      icon: Calendar,
      href: '/leave/calendar',
      color: 'bg-green-500',
    },
    {
      title: 'Process Payroll',
      description: 'Generate and review payroll reports',
      icon: DollarSign,
      href: '/payroll',
      color: 'bg-yellow-500',
    },
    {
      title: 'Performance Reviews',
      description: 'Schedule and conduct reviews',
      icon: TrendingUp,
      href: '/performance',
      color: 'bg-purple-500',
    },
  ];

  const recentActivities = [
    {
      type: 'Employee',
      description: 'New employee John Doe added to Engineering department',
      time: '2 hours ago',
      user: 'HR Manager',
    },
    {
      type: 'Leave',
      description: 'Leave request approved for Sarah Johnson',
      time: '4 hours ago',
      user: 'Department Head',
    },
    {
      type: 'Department',
      description: 'Marketing department budget updated',
      time: '6 hours ago',
      user: 'Finance Admin',
    },
    {
      type: 'Recruitment',
      description: 'New job posting created for Senior Developer',
      time: '1 day ago',
      user: 'Recruiter',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Welcome back, {user?.first_name || user?.username}!
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Here's what's happening with your HRMS today.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            <Plus className="h-4 w-4 mr-2" />
            Quick Action
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Quick Actions */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {quickActions.map((action) => (
              <QuickAction key={action.title} {...action} />
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Recent Activity
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="space-y-4">
              {recentActivities.map((activity, index) => (
                <RecentActivity key={index} {...activity} />
              ))}
            </div>
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button className="w-full text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300 font-medium">
                View all activity
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Sections */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Leave Overview */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Leave Overview
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Pending Approvals</span>
              <span className="text-lg font-semibold text-yellow-600 dark:text-yellow-400">23</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Approved This Month</span>
              <span className="text-lg font-semibold text-green-600 dark:text-green-400">156</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Rejected This Month</span>
              <span className="text-lg font-semibold text-red-600 dark:text-red-400">8</span>
            </div>
          </div>
        </div>

        {/* Department Stats */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Department Stats
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Engineering</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">342</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Sales</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">156</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Marketing</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">89</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">HR</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">45</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
