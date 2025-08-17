import React, { useState } from 'react';
import { Check, Star, Zap, Shield, Users, Building2, Database, CreditCard } from 'lucide-react';
import { useTenant } from '../../contexts/TenantContext';
import toast from 'react-hot-toast';

interface SubscriptionPlansProps {
  onPlanSelect?: (planType: string) => void;
  showCurrentPlan?: boolean;
  className?: string;
}

const planFeatures = {
  free: [
    'Up to 3 users',
    'Up to 10 employees',
    '1 GB storage',
    'Core HR features',
    'Community support',
    'Basic reporting'
  ],
  basic: [
    'Up to 10 users',
    'Up to 50 employees',
    '5 GB storage',
    'Leave management',
    'Attendance tracking',
    'Email support',
    'Advanced reporting'
  ],
  professional: [
    'Up to 25 users',
    'Up to 200 employees',
    '20 GB storage',
    'Payroll management',
    'Performance reviews',
    'Priority support',
    'Custom workflows',
    'API access'
  ],
  enterprise: [
    'Up to 100 users',
    'Up to 1000 employees',
    '100 GB storage',
    'Recruitment tools',
    'Training management',
    'Document management',
    'Dedicated support',
    'Custom integrations',
    'Advanced security',
    'Compliance features'
  ]
};

const planIcons = {
  free: Users,
  basic: Building2,
  professional: Zap,
  enterprise: Shield
};

const planColors = {
  free: 'from-gray-400 to-gray-600',
  basic: 'from-blue-400 to-blue-600',
  professional: 'from-purple-400 to-purple-600',
  enterprise: 'from-indigo-500 to-indigo-700'
};

export default function SubscriptionPlans({ 
  onPlanSelect, 
  showCurrentPlan = true,
  className = '' 
}: SubscriptionPlansProps) {
  const { tenant, subscriptionPlans, updateSubscription } = useTenant();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const handlePlanSelect = async (planType: string) => {
    if (!tenant) return;

    // Don't allow downgrading to free plan if currently on paid plan
    if (planType === 'free' && tenant.plan !== 'free') {
      toast.error('Cannot downgrade to free plan. Please contact support.');
      return;
    }

    // Don't allow selecting current plan
    if (planType === tenant.plan) {
      toast.error('This is your current plan');
      return;
    }

    setSelectedPlan(planType);
    
    if (onPlanSelect) {
      onPlanSelect(planType);
    }
  };

  const handlePlanUpgrade = async () => {
    if (!selectedPlan || !tenant) return;

    try {
      setIsUpdating(true);
      await updateSubscription(selectedPlan, 'Plan upgrade requested by user');
      setSelectedPlan(null);
      toast.success('Subscription updated successfully!');
    } catch (error) {
      console.error('Failed to update subscription:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const getPlanPrice = (plan: any) => {
    if (billingCycle === 'yearly') {
      return plan.yearly_price || plan.monthly_price * 12;
    }
    return plan.monthly_price;
  };

  const getPlanSavings = (plan: any) => {
    if (billingCycle === 'yearly' && plan.yearly_price && plan.monthly_price) {
      const monthlyTotal = plan.monthly_price * 12;
      const savings = monthlyTotal - plan.yearly_price;
      return Math.round((savings / monthlyTotal) * 100);
    }
    return 0;
  };

  if (!tenant || subscriptionPlans.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-2 text-gray-600">Loading subscription plans...</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Billing Cycle Toggle */}
      <div className="flex justify-center">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingCycle === 'monthly'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingCycle === 'yearly'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            Yearly
            {billingCycle === 'yearly' && (
              <span className="ml-1 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                Save up to 20%
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {subscriptionPlans.map((plan) => {
          const IconComponent = planIcons[plan.plan_type as keyof typeof planIcons] || Users;
          const isCurrentPlan = tenant.plan === plan.plan_type;
          const isSelected = selectedPlan === plan.plan_type;
          const isUpgrade = plan.plan_type !== 'free' && tenant.plan === 'free';
          const isDowngrade = plan.plan_type === 'free' && tenant.plan !== 'free';

          return (
            <div
              key={plan.plan_type}
              className={`relative rounded-xl border-2 transition-all duration-200 ${
                isCurrentPlan
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : isSelected
                  ? 'border-primary-500 border-dashed'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              } ${isDowngrade ? 'opacity-50' : ''}`}
            >
              {/* Current Plan Badge */}
              {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                    Current Plan
                  </span>
                </div>
              )}

              {/* Featured Plan Badge */}
              {plan.plan_type === 'professional' && (
                <div className="absolute -top-3 right-4">
                  <span className="bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center">
                    <Star className="w-3 h-3 mr-1" />
                    Popular
                  </span>
                </div>
              )}

              <div className="p-6">
                {/* Plan Header */}
                <div className="text-center mb-6">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-r ${planColors[plan.plan_type as keyof typeof planColors]} text-white mb-4`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {plan.description}
                  </p>
                  
                  {/* Pricing */}
                  <div className="mb-4">
                    <div className="flex items-baseline justify-center">
                      <span className="text-3xl font-bold text-gray-900 dark:text-white">
                        ${getPlanPrice(plan)}
                      </span>
                      <span className="text-gray-600 dark:text-gray-400 ml-1">
                        /{billingCycle === 'yearly' ? 'year' : 'month'}
                      </span>
                    </div>
                    {getPlanSavings(plan) > 0 && (
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                        Save {getPlanSavings(plan)}% with yearly billing
                      </p>
                    )}
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-3 mb-6">
                  {planFeatures[plan.plan_type as keyof typeof planFeatures]?.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* Limits */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-3 gap-4 text-center text-sm">
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{plan.max_users}</div>
                      <div className="text-gray-600 dark:text-gray-400">Users</div>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{plan.max_employees}</div>
                      <div className="text-gray-600 dark:text-gray-400">Employees</div>
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 dark:text-white">{plan.max_storage_gb}GB</div>
                      <div className="text-gray-600 dark:text-gray-400">Storage</div>
                    </div>
                  </div>
                </div>

                {/* Action Button */}
                {!isCurrentPlan ? (
                  <button
                    onClick={() => handlePlanSelect(plan.plan_type)}
                    disabled={isDowngrade || isUpdating}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                      isDowngrade
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : isSelected
                        ? 'bg-primary-600 text-white hover:bg-primary-700'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                    }`}
                  >
                    {isDowngrade ? 'Contact Support' : isSelected ? 'Selected' : 'Select Plan'}
                  </button>
                ) : (
                  <div className="text-center py-3 px-4 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-lg font-medium">
                    Current Plan
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Upgrade Button */}
      {selectedPlan && selectedPlan !== tenant.plan && (
        <div className="text-center">
          <button
            onClick={handlePlanUpgrade}
            disabled={isUpdating}
            className="bg-primary-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUpdating ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Updating...
              </div>
            ) : (
              `Upgrade to ${subscriptionPlans.find(p => p.plan_type === selectedPlan)?.name}`
            )}
          </button>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
            Your subscription will be updated immediately
          </p>
        </div>
      )}

      {/* Additional Information */}
      <div className="text-center text-sm text-gray-600 dark:text-gray-400">
        <p>
          All plans include core HR features, data backup, and security compliance.
          <br />
          Need a custom plan? <button className="text-primary-600 hover:text-primary-700 underline">Contact sales</button>
        </p>
      </div>
    </div>
  );
}
