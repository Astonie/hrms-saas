/**
 * Department Service - Handles all department-related API calls
 */

import { apiService } from './api';
import type { 
  Department, 
  DepartmentCreate, 
  DepartmentUpdate, 
  DepartmentFilters,
  DepartmentTree,
  PaginatedResponse 
} from '../types';

export class DepartmentService {
  private basePath = '/departments';

  async getDepartments(filters: DepartmentFilters = {}): Promise<PaginatedResponse<Department>> {
    return apiService.get<PaginatedResponse<Department>>(this.basePath, filters);
  }

  async getDepartment(id: string): Promise<Department> {
    return apiService.get<Department>(`${this.basePath}/${id}`);
  }

  async createDepartment(data: DepartmentCreate): Promise<Department> {
    return apiService.post<Department>(this.basePath, data);
  }

  async updateDepartment(id: string, data: DepartmentUpdate): Promise<Department> {
    return apiService.patch<Department>(`${this.basePath}/${id}`, data);
  }

  async deleteDepartment(id: string): Promise<void> {
    return apiService.delete<void>(`${this.basePath}/${id}`);
  }

  async getDepartmentTree(): Promise<DepartmentTree[]> {
    return apiService.get<DepartmentTree[]>(`${this.basePath}/tree`);
  }

  async getAllDepartments(): Promise<Department[]> {
    const response = await this.getDepartments({ limit: 1000 });
    return response.items;
  }

  async getDepartmentsByParent(parentId: string): Promise<Department[]> {
    const response = await this.getDepartments({ parent_department_id: parentId });
    return response.items;
  }

  async getDepartmentStats(id: string): Promise<{
    employee_count: number;
    active_employees: number;
    total_budget: number;
    avg_salary: number;
    children_count: number;
  }> {
    return apiService.get(`${this.basePath}/${id}/stats`);
  }

  async searchDepartments(query: string): Promise<Department[]> {
    const response = await this.getDepartments({ search: query });
    return response.items;
  }
}

export const departmentService = new DepartmentService();
