import React, { useState } from 'react';
import { 
  Users, 
  Building2, 
  Database, 
  CreditCard, 
  Calendar, 
  Shield, 
  Zap, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Settings
} from 'lucide-react';
import { useTenant } from '../../contexts/TenantContext';
import { useTheme } from '../../contexts/ThemeContext';

interface TenantDashboardProps {
  className?: string;
}

export default function TenantDashboard({ className = '' }: TenantDashboardProps) {
  const { tenant, getUsageStats, getAvailableModules } = useTenant();
  const { theme } = useTheme();
  const [activeTab, setActiveTab] = useState<'overview' | 'usage' | 'modules' | 'billing'>('overview');

  if (!tenant) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-2 text-gray-600">Loading tenant information...</p>
      </div>
    );
  }

  const usageStats = getUsageStats();
  const availableModules = getAvailableModules();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400';
      case 'trial':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400';
      case 'suspended':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'enterprise':
        return 'from-indigo-500 to-purple-600';
      case 'professional':
        return 'from-purple-500 to-pink-600';
      case 'basic':
        return 'from-blue-500 to-cyan-600';
      case 'free':
        return 'from-gray-500 to-gray-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    if (percentage >= 50) return 'text-blue-600';
    return 'text-green-600';
  };

  const getUsageBarColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    if (percentage >= 50) return 'bg-blue-500';
    return 'bg-green-500';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {tenant.name}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Tenant Dashboard • {tenant.slug}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(tenant.status)}`}>
              {tenant.status.charAt(0).toUpperCase() + tenant.status.slice(1)}
            </span>
            {tenant.is_trial && tenant.days_until_trial_end !== undefined && (
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                {tenant.days_until_trial_end} days left in trial
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview', icon: TrendingUp },
              { id: 'usage', label: 'Usage', icon: Database },
              { id: 'modules', label: 'Modules', icon: Zap },
              { id: 'billing', label: 'Billing', icon: CreditCard }
            ].map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <IconComponent className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Current Plan */}
              <div className="bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-900/10 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Current Plan: {tenant.plan.charAt(0).toUpperCase() + tenant.plan.slice(1)}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {tenant.monthly_rate ? `$${tenant.monthly_rate}/month` : 'Free plan'}
                    </p>
                  </div>
                  <div className={`w-16 h-16 rounded-full bg-gradient-to-r ${getPlanColor(tenant.plan)} flex items-center justify-center`}>
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  {
                    label: 'Users',
                    current: tenant.current_users,
                    max: tenant.max_users,
                    icon: Users,
                    color: 'text-blue-600'
                  },
                  {
                    label: 'Employees',
                    current: tenant.current_employees,
                    max: tenant.max_employees,
                    icon: Building2,
                    color: 'text-green-600'
                  },
                  {
                    label: 'Storage',
                    current: `${tenant.current_storage_gb} GB`,
                    max: `${tenant.max_storage_gb} GB`,
                    icon: Database,
                    color: 'text-purple-600'
                  }
                ].map((stat, index) => {
                  const IconComponent = stat.icon;
                  const percentage = usageStats[index]?.percentage || 0;
                  
                  return (
                    <div key={stat.label} className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-6">
                      <div className="flex items-center">
                        <div className={`p-2 rounded-lg bg-gray-100 dark:bg-gray-600 ${stat.color}`}>
                          <IconComponent className="w-6 h-6" />
                        </div>
                        <div className="ml-4">
                          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                            {stat.label}
                          </p>
                          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                            {stat.current} / {stat.max}
                          </p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-gray-600 dark:text-gray-400">Usage</span>
                          <span className={`font-medium ${getUsageColor(percentage)}`}>
                            {percentage.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${getUsageBarColor(percentage)}`}
                            style={{ width: `${Math.min(percentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Trial Status */}
              {tenant.is_trial && tenant.days_until_trial_end !== undefined && (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-3" />
                    <div>
                      <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                        Trial Period Active
                      </h4>
                      <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                        Your trial ends in {tenant.days_until_trial_end} days. 
                        <button className="ml-2 text-yellow-800 dark:text-yellow-200 underline hover:no-underline">
                          Upgrade now
                        </button>
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Support Tier */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                      Support Tier: {tenant.support_tier.charAt(0).toUpperCase() + tenant.support_tier.slice(1)}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {tenant.support_tier === 'dedicated' && 'Dedicated account manager and priority support'}
                      {tenant.support_tier === 'priority' && 'Priority support with faster response times'}
                      {tenant.support_tier === 'email' && 'Email support during business hours'}
                      {tenant.support_tier === 'community' && 'Community support and documentation'}
                    </p>
                  </div>
                  <Settings className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>
          )}

          {/* Usage Tab */}
          {activeTab === 'usage' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Resource Usage
              </h3>
              
              <div className="space-y-4">
                {usageStats.map((stat, index) => {
                  const labels = ['Users', 'Employees', 'Storage (GB)'];
                  const icons = [Users, Building2, Database];
                  const IconComponent = icons[index];
                  
                  return (
                    <div key={labels[index]} className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          <IconComponent className="w-5 h-5 text-gray-400 mr-2" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            {labels[index]}
                          </span>
                        </div>
                        <span className={`text-sm font-medium ${getUsageColor(stat.percentage)}`}>
                          {stat.current} / {stat.max}
                        </span>
                      </div>
                      
                      <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full ${getUsageBarColor(stat.percentage)} transition-all duration-300`}
                          style={{ width: `${Math.min(stat.percentage, 100)}%` }}
                        ></div>
                      </div>
                      
                      <div className="flex items-center justify-between mt-2 text-sm">
                        <span className="text-gray-600 dark:text-gray-400">
                          {stat.percentage.toFixed(1)}% used
                        </span>
                        {stat.percentage >= 90 && (
                          <span className="text-red-600 flex items-center">
                            <AlertTriangle className="w-4 h-4 mr-1" />
                            Near limit
                          </span>
                        )}
                        {stat.percentage >= 75 && stat.percentage < 90 && (
                          <span className="text-yellow-600 flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            Monitor usage
                          </span>
                        )}
                        {stat.percentage < 75 && (
                          <span className="text-green-600 flex items-center">
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Healthy
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Modules Tab */}
          {activeTab === 'modules' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Available Modules
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {availableModules.map((module) => (
                  <div
                    key={module.name}
                    className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                          {module.display_name}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {module.description}
                        </p>
                        
                        {/* Permissions */}
                        <div className="mb-3">
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">
                            Permissions
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {module.permissions.slice(0, 3).map((permission) => (
                              <span
                                key={permission}
                                className="px-2 py-1 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded"
                              >
                                {permission}
                              </span>
                            ))}
                            {module.permissions.length > 3 && (
                              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 text-xs rounded">
                                +{module.permissions.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Features */}
                        <div>
                          <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 uppercase tracking-wide">
                            Features
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {module.features.slice(0, 2).map((feature) => (
                              <span
                                key={feature}
                                className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded"
                              >
                                {feature}
                              </span>
                            ))}
                            {module.features.length > 2 && (
                              <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded">
                                +{module.features.length - 2} more
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="ml-3">
                        <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                          <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Billing Tab */}
          {activeTab === 'billing' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Billing Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Current Plan Details */}
                <div className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-6">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Current Plan</h4>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Plan</span>
                      <span className="font-medium text-gray-900 dark:text-white capitalize">
                        {tenant.plan}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Billing Cycle</span>
                      <span className="font-medium text-gray-900 dark:text-white capitalize">
                        {tenant.billing_cycle}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Monthly Rate</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {tenant.monthly_rate ? `$${tenant.monthly_rate}` : 'Free'}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Currency</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {tenant.currency}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Subscription Dates */}
                <div className="bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-6">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Subscription Dates</h4>
                  
                  <div className="space-y-3">
                    {tenant.subscription_start_date && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Start Date</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {new Date(tenant.subscription_start_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    
                    {tenant.subscription_end_date && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">End Date</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {new Date(tenant.subscription_end_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    
                    {tenant.trial_end_date && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Trial Ends</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {new Date(tenant.trial_end_date).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Auto Renew</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {tenant.auto_renew ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h4 className="font-medium text-gray-900 dark:text-white mb-4">Actions</h4>
                
                <div className="flex flex-wrap gap-3">
                  <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                    Upgrade Plan
                  </button>
                  <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    View Invoices
                  </button>
                  <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    Update Billing
                  </button>
                  <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                    Contact Support
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
