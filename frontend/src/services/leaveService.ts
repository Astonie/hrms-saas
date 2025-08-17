/**
 * Leave Service - Handles all leave management API calls
 */

import { apiService } from './api';
import type { 
  LeaveRequest, 
  LeaveRequestCreate, 
  LeaveRequestUpdate, 
  LeaveApproval,
  LeaveBalance,
  LeaveFilters,
  PaginatedResponse 
} from '../types';

export class LeaveService {
  private basePath = '/leave';

  // Leave Requests
  async getLeaveRequests(filters: LeaveFilters = {}): Promise<PaginatedResponse<LeaveRequest>> {
    return apiService.get<PaginatedResponse<LeaveRequest>>(`${this.basePath}/requests`, filters);
  }

  async getLeaveRequest(id: string): Promise<LeaveRequest> {
    return apiService.get<LeaveRequest>(`${this.basePath}/requests/${id}`);
  }

  async createLeaveRequest(data: LeaveRequestCreate): Promise<LeaveRequest> {
    return apiService.post<LeaveRequest>(`${this.basePath}/requests`, data);
  }

  async updateLeaveRequest(id: string, data: LeaveRequestUpdate): Promise<LeaveRequest> {
    return apiService.patch<LeaveRequest>(`${this.basePath}/requests/${id}`, data);
  }

  async deleteLeaveRequest(id: string): Promise<void> {
    return apiService.delete<void>(`${this.basePath}/requests/${id}`);
  }

  async approveLeaveRequest(id: string, data: LeaveApproval): Promise<LeaveRequest> {
    return apiService.post<LeaveRequest>(`${this.basePath}/requests/${id}/approve`, data);
  }

  async rejectLeaveRequest(id: string, notes?: string): Promise<LeaveRequest> {
    return apiService.post<LeaveRequest>(`${this.basePath}/requests/${id}/reject`, { notes });
  }

  async cancelLeaveRequest(id: string, notes?: string): Promise<LeaveRequest> {
    return apiService.post<LeaveRequest>(`${this.basePath}/requests/${id}/cancel`, { notes });
  }

  // Leave Balances
  async getLeaveBalances(employeeId?: string, year?: number): Promise<LeaveBalance[]> {
    const params: any = {};
    if (employeeId) params.employee_id = employeeId;
    if (year) params.year = year;
    
    return apiService.get<LeaveBalance[]>(`${this.basePath}/balances`, params);
  }

  async updateLeaveBalance(id: string, data: Partial<LeaveBalance>): Promise<LeaveBalance> {
    return apiService.patch<LeaveBalance>(`${this.basePath}/balances/${id}`, data);
  }

  // Leave Calendar
  async getLeaveCalendar(startDate: string, endDate: string, departmentId?: string): Promise<{
    date: string;
    employees_on_leave: {
      id: string;
      name: string;
      leave_type: string;
      is_half_day: boolean;
    }[];
  }[]> {
    const params: any = { start_date: startDate, end_date: endDate };
    if (departmentId) params.department_id = departmentId;
    
    return apiService.get(`${this.basePath}/calendar`, params);
  }

  // Leave Analytics
  async getLeaveAnalytics(year?: number, departmentId?: string): Promise<{
    total_requests: number;
    approved_requests: number;
    rejected_requests: number;
    pending_requests: number;
    total_days_taken: number;
    average_days_per_employee: number;
    leave_type_breakdown: { [key: string]: number };
    monthly_trends: { month: string; requests: number; days: number }[];
  }> {
    const params: any = {};
    if (year) params.year = year;
    if (departmentId) params.department_id = departmentId;
    
    return apiService.get(`${this.basePath}/analytics`, params);
  }

  // My Leave Requests (for current user)
  async getMyLeaveRequests(filters: Omit<LeaveFilters, 'employee_id'> = {}): Promise<PaginatedResponse<LeaveRequest>> {
    return apiService.get<PaginatedResponse<LeaveRequest>>(`${this.basePath}/my-requests`, filters);
  }

  async getMyLeaveBalances(year?: number): Promise<LeaveBalance[]> {
    const params = year ? { year } : {};
    return apiService.get<LeaveBalance[]>(`${this.basePath}/my-balances`, params);
  }

  // Leave requests pending approval for managers
  async getPendingApprovals(filters: LeaveFilters = {}): Promise<PaginatedResponse<LeaveRequest>> {
    return apiService.get<PaginatedResponse<LeaveRequest>>(`${this.basePath}/pending-approvals`, filters);
  }

  // Calculate leave days
  async calculateLeaveDays(data: {
    start_date: string;
    end_date: string;
    start_time?: string;
    end_time?: string;
    is_half_day?: boolean;
  }): Promise<{ total_days: number; working_days: number }> {
    return apiService.post(`${this.basePath}/calculate-days`, data);
  }
}

export const leaveService = new LeaveService();
