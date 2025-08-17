/**
 * Centralized export for all services
 */

export * from './api';
export * from './employeeService';
export * from './departmentService';
export * from './leaveService';
export * from './dashboardService';

// Re-export service instances for easy access
export { apiService } from './api';
export { employeeService } from './employeeService';
export { departmentService } from './departmentService';
export { leaveService } from './leaveService';
export { dashboardService } from './dashboardService';
