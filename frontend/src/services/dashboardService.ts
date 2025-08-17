/**
 * Dashboard Service - Handles all dashboard and analytics API calls
 */

import { apiService } from './api';
import type { DashboardStats, RecentActivity } from '../types';

export class DashboardService {
  private basePath = '/dashboard';

  async getDashboardStats(): Promise<DashboardStats> {
    return apiService.get<DashboardStats>(`${this.basePath}/stats`);
  }

  async getRecentActivity(limit = 10): Promise<RecentActivity[]> {
    return apiService.get<RecentActivity[]>(`${this.basePath}/activity`, { limit });
  }

  async getEmployeeGrowth(period = '12months'): Promise<{
    labels: string[];
    datasets: {
      label: string;
      data: number[];
    }[];
  }> {
    return apiService.get(`${this.basePath}/employee-growth`, { period });
  }

  async getDepartmentDistribution(): Promise<{
    name: string;
    count: number;
    percentage: number;
  }[]> {
    return apiService.get(`${this.basePath}/department-distribution`);
  }

  async getLeaveOverview(): Promise<{
    total_requests: number;
    approved: number;
    pending: number;
    rejected: number;
    monthly_trend: { month: string; requests: number }[];
  }> {
    return apiService.get(`${this.basePath}/leave-overview`);
  }

  async getUpcomingBirthdays(days = 30): Promise<{
    id: string;
    name: string;
    department: string;
    date: string;
    days_until: number;
  }[]> {
    return apiService.get(`${this.basePath}/upcoming-birthdays`, { days });
  }

  async getNewHires(period = '30days'): Promise<{
    count: number;
    employees: {
      id: string;
      name: string;
      department: string;
      hire_date: string;
      job_title: string;
    }[];
  }> {
    return apiService.get(`${this.basePath}/new-hires`, { period });
  }

  async getEmployeesByStatus(): Promise<{
    active: number;
    inactive: number;
    terminated: number;
    on_leave: number;
  }> {
    return apiService.get(`${this.basePath}/employees-by-status`);
  }
}

export const dashboardService = new DashboardService();
