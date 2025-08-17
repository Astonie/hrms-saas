import React from 'react';
import { useDashboardData } from '../../hooks/useApi';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

export default function Dashboard() {
  const { data: stats, isLoading, error } = useDashboardData();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600 mb-4">Failed to load dashboard data</p>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
        
        {stats ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-blue-600">Total Employees</h3>
              <p className="text-2xl font-bold text-blue-900">{stats.total_employees || 0}</p>
            </div>
            
            <div className="bg-green-50 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-green-600">Active Employees</h3>
              <p className="text-2xl font-bold text-green-900">{stats.active_employees || 0}</p>
            </div>
            
            <div className="bg-purple-50 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-purple-600">Departments</h3>
              <p className="text-2xl font-bold text-purple-900">{stats.total_departments || 0}</p>
            </div>
            
            <div className="bg-orange-50 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-orange-600">Pending Leave Requests</h3>
              <p className="text-2xl font-bold text-orange-900">{stats.pending_leave_requests || 0}</p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500">No dashboard data available</p>
        )}
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Welcome to HRMS-SAAS</h2>
        <p className="text-gray-600">
          Your comprehensive Human Resource Management System is ready to use. 
          Navigate through the sidebar to manage employees, departments, and leave requests.
        </p>
      </div>
    </div>
  );
}
