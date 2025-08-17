/**
 * Custom React hooks for HRMS data fetching and state management
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  employeeService, 
  departmentService, 
  leaveService, 
  dashboardService,
  APIError 
} from '../services';
import type { 
  Employee, 
  Department, 
  LeaveRequest, 
  DashboardStats,
  PaginatedResponse,
  EmployeeFilters,
  LeaveFilters 
} from '../types';

// Generic hook for paginated data
export function usePaginatedData<T, F extends { page?: number; limit?: number }>(
  fetcher: (filters: F) => Promise<PaginatedResponse<T>>,
  initialFilters: F = {} as F
) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  });
  const [filters, setFilters] = useState<F>(initialFilters);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetcher({ ...filters, page: pagination.page, limit: pagination.limit });
      setData(response.items);
      setPagination({
        page: response.page,
        limit: response.limit,
        total: response.total,
        pages: response.pages
      });
    } catch (err) {
      const errorMessage = err instanceof APIError ? err.message : 'An error occurred';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [fetcher, filters, pagination.page, pagination.limit]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const updateFilters = useCallback((newFilters: Partial<F>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  }, []);

  const changePage = useCallback((page: number) => {
    setPagination(prev => ({ ...prev, page }));
  }, []);

  const refresh = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    pagination,
    filters,
    updateFilters,
    changePage,
    refresh
  };
}

// Employee hooks
export function useEmployees(initialFilters: EmployeeFilters = {}) {
  return usePaginatedData(employeeService.getEmployees.bind(employeeService), initialFilters);
}

export function useEmployee(id: string) {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchEmployee = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await employeeService.getEmployee(id);
        setEmployee(data);
      } catch (err) {
        const errorMessage = err instanceof APIError ? err.message : 'Failed to load employee';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchEmployee();
  }, [id]);

  const refresh = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await employeeService.getEmployee(id);
      setEmployee(data);
    } catch (err) {
      const errorMessage = err instanceof APIError ? err.message : 'Failed to reload employee';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [id]);

  return { employee, loading, error, refresh };
}

// Department hooks
export function useDepartments() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await departmentService.getAllDepartments();
        setDepartments(data);
      } catch (err) {
        const errorMessage = err instanceof APIError ? err.message : 'Failed to load departments';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchDepartments();
  }, []);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await departmentService.getAllDepartments();
      setDepartments(data);
    } catch (err) {
      const errorMessage = err instanceof APIError ? err.message : 'Failed to reload departments';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return { departments, loading, error, refresh };
}

// Leave hooks
export function useLeaveRequests(initialFilters: LeaveFilters = {}) {
  return usePaginatedData(leaveService.getLeaveRequests.bind(leaveService), initialFilters);
}

export function useMyLeaveRequests(initialFilters: Omit<LeaveFilters, 'employee_id'> = {}) {
  return usePaginatedData(leaveService.getMyLeaveRequests.bind(leaveService), initialFilters);
}

export function useLeaveBalances(employeeId?: string, year?: number) {
  const [balances, setBalances] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalances = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await leaveService.getLeaveBalances(employeeId, year);
        setBalances(data);
      } catch (err) {
        const errorMessage = err instanceof APIError ? err.message : 'Failed to load leave balances';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchBalances();
  }, [employeeId, year]);

  return { balances, loading, error };
}

// Dashboard hooks
export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await dashboardService.getDashboardStats();
        setStats(data);
      } catch (err) {
        const errorMessage = err instanceof APIError ? err.message : 'Failed to load dashboard stats';
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const data = await dashboardService.getDashboardStats();
      setStats(data);
    } catch (err) {
      const errorMessage = err instanceof APIError ? err.message : 'Failed to reload dashboard stats';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return { stats, loading, error, refresh };
}

// Generic mutation hook for creating/updating data
export function useMutation<T, D>(
  mutationFn: (data: D) => Promise<T>,
  onSuccess?: (data: T) => void,
  onError?: (error: APIError) => void
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(async (data: D) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mutationFn(data);
      onSuccess?.(result);
      return result;
    } catch (err) {
      const apiError = err instanceof APIError ? err : new APIError('An error occurred', 500);
      setError(apiError.message);
      onError?.(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, [mutationFn, onSuccess, onError]);

  return { mutate, loading, error };
}

// Specific mutation hooks
export function useCreateEmployee(onSuccess?: (employee: Employee) => void) {
  return useMutation(employeeService.createEmployee.bind(employeeService), onSuccess);
}

export function useUpdateEmployee(onSuccess?: (employee: Employee) => void) {
  return useMutation(
    ({ id, data }: { id: string; data: any }) => employeeService.updateEmployee(id, data),
    onSuccess
  );
}

export function useCreateLeaveRequest(onSuccess?: (request: LeaveRequest) => void) {
  return useMutation(leaveService.createLeaveRequest.bind(leaveService), onSuccess);
}

export function useApproveLeaveRequest(onSuccess?: (request: LeaveRequest) => void) {
  return useMutation(
    ({ id, data }: { id: string; data: any }) => leaveService.approveLeaveRequest(id, data),
    onSuccess
  );
}

// Dashboard hooks
export function useDashboardData() {
  const [data, setData] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const stats = await dashboardService.getDashboardStats();
      setData(stats);
    } catch (err) {
      console.warn('Dashboard data not available:', err);
      setError(err instanceof Error ? err : new Error('Failed to load dashboard data'));
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}
