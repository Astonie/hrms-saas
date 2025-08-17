/**
 * Employee Service - Handles all employee-related API calls
 */

import { apiService } from './api';
import type { 
  Employee, 
  EmployeeCreate, 
  EmployeeUpdate, 
  EmployeeFilters,
  PaginatedResponse 
} from '../types';

export class EmployeeService {
  private basePath = '/employees';

  async getEmployees(filters: EmployeeFilters = {}): Promise<PaginatedResponse<Employee>> {
    return apiService.get<PaginatedResponse<Employee>>(this.basePath, filters);
  }

  async getEmployee(id: string): Promise<Employee> {
    return apiService.get<Employee>(`${this.basePath}/${id}`);
  }

  async createEmployee(data: EmployeeCreate): Promise<Employee> {
    return apiService.post<Employee>(this.basePath, data);
  }

  async updateEmployee(id: string, data: EmployeeUpdate): Promise<Employee> {
    return apiService.patch<Employee>(`${this.basePath}/${id}`, data);
  }

  async deleteEmployee(id: string): Promise<void> {
    return apiService.delete<void>(`${this.basePath}/${id}`);
  }

  async searchEmployees(query: string, limit = 10): Promise<Employee[]> {
    const response = await this.getEmployees({ search: query, limit });
    return response.items;
  }

  async getEmployeesByDepartment(departmentId: string): Promise<Employee[]> {
    const response = await this.getEmployees({ department_id: departmentId });
    return response.items;
  }

  async getEmployeeHierarchy(employeeId: string): Promise<{
    supervisor?: Employee;
    subordinates: Employee[];
    manager?: Employee;
    teamMembers: Employee[];
  }> {
    return apiService.get(`${this.basePath}/${employeeId}/hierarchy`);
  }

  async exportEmployees(filters: EmployeeFilters = {}): Promise<Blob> {
    const params = new URLSearchParams(filters as any);
    const response = await fetch(`http://localhost:8000/api/v1${this.basePath}/export?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'X-Tenant-ID': localStorage.getItem('tenantId') || '',
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to export employees');
    }
    
    return response.blob();
  }
}

export const employeeService = new EmployeeService();
