/**
 * TypeScript interfaces for HRMS-SAAS data models
 * Matches backend Pydantic models for type safety
 */

// Common types
export interface PaginationParams {
  page?: number;
  limit?: number;
  search?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Employee interfaces
export interface Employee {
  id: string;
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  
  // Employment details
  employment_status: 'ACTIVE' | 'INACTIVE' | 'TERMINATED' | 'ON_LEAVE';
  employment_type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERN' | 'TEMPORARY';
  hire_date: string;
  probation_end_date?: string;
  termination_date?: string;
  
  // Position
  job_title: string;
  department_id?: string;
  department_name?: string;
  supervisor_id?: string;
  supervisor_name?: string;
  manager_id?: string;
  manager_name?: string;
  
  // Compensation
  base_salary?: number;
  hourly_rate?: number;
  currency: string;
  pay_frequency?: string;
  
  // Personal details
  marital_status?: 'SINGLE' | 'MARRIED' | 'DIVORCED' | 'WIDOWED' | 'SEPARATED';
  blood_type?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  
  // System fields
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  
  employment_status?: Employee['employment_status'];
  employment_type?: Employee['employment_type'];
  hire_date: string;
  job_title: string;
  department_id?: string;
  supervisor_id?: string;
  manager_id?: string;
  
  base_salary?: number;
  hourly_rate?: number;
  currency?: string;
  pay_frequency?: string;
  
  marital_status?: Employee['marital_status'];
  blood_type?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {}

// Department interfaces
export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  parent_department_id?: string;
  parent_department_name?: string;
  department_head_id?: string;
  department_head_name?: string;
  is_active: boolean;
  budget?: number;
  location?: string;
  employee_count: number;
  created_at: string;
  updated_at: string;
}

export interface DepartmentCreate {
  name: string;
  code: string;
  description?: string;
  parent_department_id?: string;
  department_head_id?: string;
  budget?: number;
  location?: string;
}

export interface DepartmentUpdate extends Partial<DepartmentCreate> {}

export interface DepartmentTree {
  id: string;
  name: string;
  code: string;
  employee_count: number;
  children: DepartmentTree[];
}

// Leave interfaces
export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  department_name?: string;
  leave_type: 'ANNUAL' | 'SICK' | 'MATERNITY' | 'PATERNITY' | 'PERSONAL' | 'BEREAVEMENT' | 'EMERGENCY' | 'UNPAID';
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  is_half_day: boolean;
  reason: string;
  notes?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  requested_days: number;
  approved_days?: number;
  approver_id?: string;
  approver_name?: string;
  approval_date?: string;
  approval_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequestCreate {
  employee_id?: string;
  leave_type: LeaveRequest['leave_type'];
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  is_half_day?: boolean;
  reason: string;
  notes?: string;
}

export interface LeaveRequestUpdate {
  start_date?: string;
  end_date?: string;
  start_time?: string;
  end_time?: string;
  is_half_day?: boolean;
  reason?: string;
  notes?: string;
}

export interface LeaveApproval {
  approved_days: number;
  notes?: string;
}

export interface LeaveBalance {
  id: string;
  employee_id: string;
  leave_type: LeaveRequest['leave_type'];
  year: number;
  total_days: number;
  used_days: number;
  pending_days: number;
  remaining_days: number;
  carried_over_days: number;
}

// Dashboard interfaces
export interface DashboardStats {
  total_employees: number;
  active_employees: number;
  departments_count: number;
  pending_leave_requests: number;
  total_leave_requests_this_month: number;
  new_hires_this_month: number;
  upcoming_birthdays: number;
}

export interface RecentActivity {
  id: string;
  type: 'employee_created' | 'leave_requested' | 'leave_approved' | 'department_created';
  title: string;
  description: string;
  user_name: string;
  timestamp: string;
}

// Filter and search interfaces
export interface EmployeeFilters extends PaginationParams {
  department_id?: string;
  employment_status?: string;
  employment_type?: string;
  job_title?: string;
  supervisor_id?: string;
  hire_date_from?: string;
  hire_date_to?: string;
}

export interface LeaveFilters extends PaginationParams {
  employee_id?: string;
  department_id?: string;
  leave_type?: string;
  status?: string;
  start_date_from?: string;
  start_date_to?: string;
}

export interface DepartmentFilters extends PaginationParams {
  parent_department_id?: string;
  is_active?: boolean;
}
