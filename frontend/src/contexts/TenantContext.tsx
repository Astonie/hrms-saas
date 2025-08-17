import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

// Types
interface SubscriptionPlan {
  id: number;
  name: string;
  plan_type: string;
  description: string;
  monthly_price: number | null;
  yearly_price: number | null;
  max_users: number;
  max_employees: number;
  max_storage_gb: number;
  enabled_modules: string[];
  trial_days: number;
  support_tier: string;
}

interface TenantInfo {
  id: number;
  name: string;
  slug: string;
  domain?: string;
  subdomain?: string;
  plan: string;
  status: string;
  billing_cycle: string;
  max_users: number;
  max_employees: number;
  max_storage_gb: number;
  current_users: number;
  current_employees: number;
  current_storage_gb: number;
  enabled_modules: string[];
  feature_flags: Record<string, any>;
  usage_percentage: {
    users: number;
    employees: number;
    storage: number;
  };
  is_active: boolean;
  is_trial: boolean;
  days_until_trial_end?: number;
  support_tier: string;
  monthly_rate?: number;
  subscription_start_date?: string;
  subscription_end_date?: string;
  trial_end_date?: string;
  created_at: string;
  updated_at: string;
  currency: string;
  auto_renew: boolean;
  timezone: string;
  locale: string;
}

interface ModuleDefinition {
  name: string;
  display_name: string;
  description: string;
  permissions: string[];
  features: string[];
  icon?: string;
  route_path?: string;
}

interface TenantState {
  tenant: TenantInfo | null;
  subscriptionPlans: SubscriptionPlan[];
  availableModules: ModuleDefinition[];
  isLoading: boolean;
  error: string | null;
}

interface TenantContextType extends TenantState {
  refreshTenantInfo: () => Promise<void>;
  updateSubscription: (planType: string, reason?: string) => Promise<void>;
  checkModuleAccess: (moduleName: string) => boolean;
  getAvailableModules: () => ModuleDefinition[];
  getSubscriptionPlan: () => SubscriptionPlan | null;
  getUsageStats: () => {
    current: number;
    max: number;
    percentage: number;
  }[];
}

// Action types
type TenantAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_TENANT'; payload: TenantInfo }
  | { type: 'SET_SUBSCRIPTION_PLANS'; payload: SubscriptionPlan[] }
  | { type: 'SET_AVAILABLE_MODULES'; payload: ModuleDefinition[] }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'UPDATE_TENANT'; payload: Partial<TenantInfo> };

// Initial state
const initialState: TenantState = {
  tenant: null,
  subscriptionPlans: [],
  availableModules: [],
  isLoading: true,
  error: null,
};

// Reducer
function tenantReducer(state: TenantState, action: TenantAction): TenantState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_TENANT':
      return { ...state, tenant: action.payload, error: null };
    case 'SET_SUBSCRIPTION_PLANS':
      return { ...state, subscriptionPlans: action.payload };
    case 'SET_AVAILABLE_MODULES':
      return { ...state, availableModules: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'UPDATE_TENANT':
      return { 
        ...state, 
        tenant: state.tenant ? { ...state.tenant, ...action.payload } : null 
      };
    default:
      return state;
  }
}

// Create context
const TenantContext = createContext<TenantContextType | undefined>(undefined);

// Provider component
export function TenantProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(tenantReducer, initialState);
  const { isAuthenticated, token } = useAuth();

  // Fetch tenant information on mount
  useEffect(() => {
    if (isAuthenticated && token) {
      // Temporarily use mock data to avoid 500 errors
      const mockTenant: TenantInfo = {
        id: 1,
        name: 'Demo Company',
        slug: 'demo',
        domain: 'demo.company.com',
        subdomain: 'demo',
        plan: 'professional',
        status: 'active',
        billing_cycle: 'monthly',
        max_users: 50,
        max_employees: 100,
        max_storage_gb: 10,
        current_users: 1,
        current_employees: 0,
        current_storage_gb: 0,
        enabled_modules: ['employees', 'departments', 'leave', 'dashboard'],
        feature_flags: {},
        usage_percentage: {
          users: 2,
          employees: 0,
          storage: 0
        },
        is_active: true,
        is_trial: false,
        support_tier: 'standard',
        monthly_rate: 29,
        subscription_start_date: '2025-01-01T00:00:00Z',
        subscription_end_date: '2025-12-31T23:59:59Z',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-08-17T12:00:00Z',
        currency: 'USD',
        auto_renew: true,
        timezone: 'UTC',
        locale: 'en-US'
      };
      dispatch({ type: 'SET_TENANT', payload: mockTenant });
      dispatch({ type: 'SET_LOADING', payload: false });
      
      // TODO: Re-enable these when backend issues are fixed
      // refreshTenantInfo();
      // fetchSubscriptionPlans();
    } else {
      // If not authenticated, set loading to false to prevent infinite loading
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [isAuthenticated, token]);

  // Refresh tenant information
  const refreshTenantInfo = async () => {
    if (!token) {
      dispatch({ type: 'SET_LOADING', payload: false });
      return;
    }

    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const response = await fetch('/api/v1/tenants/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const tenantData = await response.json();
        dispatch({ type: 'SET_TENANT', payload: tenantData });
        
        // Fetch available modules
        await fetchAvailableModules(tenantData.id);
      } else {
        // Don't throw error, just log and set loading to false
        console.warn('Failed to fetch tenant information:', response.status);
        dispatch({ type: 'SET_ERROR', payload: 'Unable to load tenant information' });
      }
    } catch (error) {
      console.error('Failed to refresh tenant info:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Unable to load tenant information' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  // Fetch subscription plans
  const fetchSubscriptionPlans = async () => {
    if (!token) return;

    try {
      const response = await fetch('/api/v1/tenants/subscription-plans', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const plans = await response.json();
        dispatch({ type: 'SET_SUBSCRIPTION_PLANS', payload: plans });
      }
    } catch (error) {
      console.error('Failed to fetch subscription plans:', error);
    }
  };

  // Fetch available modules for tenant
  const fetchAvailableModules = async (tenantId: number) => {
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/tenants/${tenantId}/modules`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const modules = await response.json();
        dispatch({ type: 'SET_AVAILABLE_MODULES', payload: modules });
      }
    } catch (error) {
      console.error('Failed to fetch available modules:', error);
    }
  };

  // Update subscription plan
  const updateSubscription = async (planType: string, reason?: string) => {
    if (!token || !state.tenant) return;

    try {
      const response = await fetch(`/api/v1/tenants/${state.tenant.id}/subscription`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_plan_type: planType,
          change_reason: reason,
        }),
      });

      if (response.ok) {
        const updatedTenant = await response.json();
        dispatch({ type: 'SET_TENANT', payload: updatedTenant });
        toast.success('Subscription updated successfully');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update subscription');
      }
    } catch (error) {
      console.error('Failed to update subscription:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to update subscription');
      throw error;
    }
  };

  // Check if tenant has access to a specific module
  const checkModuleAccess = (moduleName: string): boolean => {
    if (!state.tenant) return false;
    return state.tenant.enabled_modules.includes(moduleName);
  };

  // Get available modules
  const getAvailableModules = (): ModuleDefinition[] => {
    return state.availableModules;
  };

  // Get current subscription plan
  const getSubscriptionPlan = (): SubscriptionPlan | null => {
    if (!state.tenant) return null;
    return state.subscriptionPlans.find(plan => plan.plan_type === state.tenant?.plan) || null;
  };

  // Get usage statistics
  const getUsageStats = () => {
    if (!state.tenant) return [];

    return [
      {
        current: state.tenant.current_users,
        max: state.tenant.max_users,
        percentage: state.tenant.usage_percentage.users,
      },
      {
        current: state.tenant.current_employees,
        max: state.tenant.max_employees,
        percentage: state.tenant.usage_percentage.employees,
      },
      {
        current: state.tenant.current_storage_gb,
        max: state.tenant.max_storage_gb,
        percentage: state.tenant.usage_percentage.storage,
      },
    ];
  };

  const value: TenantContextType = {
    ...state,
    refreshTenantInfo,
    updateSubscription,
    checkModuleAccess,
    getAvailableModules,
    getSubscriptionPlan,
    getUsageStats,
  };

  return <TenantContext.Provider value={value}>{children}</TenantContext.Provider>;
}

// Hook to use tenant context
export function useTenant() {
  const context = useContext(TenantContext);
  if (context === undefined) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
}

// Hook to check module access
export function useModuleAccess(moduleName: string): boolean {
  const { checkModuleAccess } = useTenant();
  return checkModuleAccess(moduleName);
}

// Hook to get subscription plan
export function useSubscriptionPlan(): SubscriptionPlan | null {
  const { getSubscriptionPlan } = useTenant();
  return getSubscriptionPlan();
}

// Hook to get usage statistics
export function useUsageStats() {
  const { getUsageStats } = useTenant();
  return getUsageStats();
}
