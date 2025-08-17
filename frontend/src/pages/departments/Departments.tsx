import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Plus, 
  Search, 
  Filter, 
  Edit3, 
  Trash2, 
  Eye, 
  Users,
  MapPin,
  Mail,
  Phone,
  Calendar
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface Department {
  id: number;
  name: string;
  description: string;
  manager: string;
  managerEmail: string;
  employeeCount: number;
  budget: number;
  location: string;
  established: string;
  status: 'active' | 'inactive';
}

const mockDepartments: Department[] = [
  {
    id: 1,
    name: 'Engineering',
    description: 'Software development and technical innovation',
    manager: 'John Smith',
    managerEmail: 'john.smith@company.com',
    employeeCount: 15,
    budget: 2500000,
    location: 'Building A, Floor 3',
    established: '2020-01-15',
    status: 'active'
  },
  {
    id: 2,
    name: 'Human Resources',
    description: 'Employee relations, recruitment, and HR policies',
    manager: 'Sarah Johnson',
    managerEmail: 'sarah.johnson@company.com',
    employeeCount: 8,
    budget: 800000,
    location: 'Building B, Floor 2',
    established: '2019-06-20',
    status: 'active'
  },
  {
    id: 3,
    name: 'Marketing',
    description: 'Brand management and digital marketing strategies',
    manager: 'Michael Chen',
    managerEmail: 'michael.chen@company.com',
    employeeCount: 12,
    budget: 1200000,
    location: 'Building A, Floor 2',
    established: '2020-03-10',
    status: 'active'
  },
  {
    id: 4,
    name: 'Sales',
    description: 'Customer acquisition and revenue generation',
    manager: 'Emily Davis',
    managerEmail: 'emily.davis@company.com',
    employeeCount: 20,
    budget: 1800000,
    location: 'Building C, Floor 1',
    established: '2019-11-05',
    status: 'active'
  },
  {
    id: 5,
    name: 'Finance',
    description: 'Financial planning, analysis, and accounting',
    manager: 'Robert Wilson',
    managerEmail: 'robert.wilson@company.com',
    employeeCount: 6,
    budget: 600000,
    location: 'Building B, Floor 3',
    established: '2020-08-12',
    status: 'inactive'
  }
];

export default function Departments() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDepartments(mockDepartments);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredDepartments = departments.filter(department => {
    const matchesSearch = department.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      department.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      department.manager.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || department.status === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    return status === 'active' 
      ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
      : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
  };

  const getDepartmentIcon = (name: string) => {
    const iconClasses = "h-8 w-8";
    switch (name.toLowerCase()) {
      case 'engineering':
        return '🔧';
      case 'human resources':
        return '👥';
      case 'marketing':
        return '📢';
      case 'sales':
        return '💼';
      case 'finance':
        return '💰';
      default:
        return '🏢';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-xl">
              <Building2 className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
            Department Management
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Organize and manage your company departments
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            <Plus className="h-4 w-4" />
            Add Department
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Departments</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{departments.length}</p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Building2 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Departments</p>
              <p className="text-3xl font-bold text-green-600">{departments.filter(d => d.status === 'active').length}</p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Building2 className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Employees</p>
              <p className="text-3xl font-bold text-blue-600">{departments.reduce((sum, d) => sum + d.employeeCount, 0)}</p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Budget</p>
              <p className="text-3xl font-bold text-green-600">
                ${(departments.reduce((sum, d) => sum + d.budget, 0) / 1000000).toFixed(1)}M
              </p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search departments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as 'all' | 'active' | 'inactive')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <button className="flex items-center gap-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300">
              <Filter className="h-4 w-4" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Department Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDepartments.map((department) => (
          <div key={department.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-3xl">
                  {getDepartmentIcon(department.name)}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {department.name}
                  </h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(department.status)}`}>
                    {department.status}
                  </span>
                </div>
              </div>
              <div className="flex gap-1">
                <button className="p-1 text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">
                  <Eye className="h-4 w-4" />
                </button>
                <button className="p-1 text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">
                  <Edit3 className="h-4 w-4" />
                </button>
                <button className="p-1 text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {department.description}
            </p>

            <div className="space-y-3">
              <div className="flex items-center text-sm">
                <Users className="h-4 w-4 mr-2 text-gray-400" />
                <span className="text-gray-900 dark:text-white font-medium">{department.employeeCount} employees</span>
              </div>
              
              <div className="flex items-center text-sm">
                <Mail className="h-4 w-4 mr-2 text-gray-400" />
                <div>
                  <div className="text-gray-900 dark:text-white font-medium">{department.manager}</div>
                  <div className="text-gray-500 dark:text-gray-400">{department.managerEmail}</div>
                </div>
              </div>

              <div className="flex items-center text-sm">
                <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                <span className="text-gray-600 dark:text-gray-300">{department.location}</span>
              </div>

              <div className="flex items-center text-sm">
                <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                <span className="text-gray-600 dark:text-gray-300">
                  Est. {new Date(department.established).getFullYear()}
                </span>
              </div>

              <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Annual Budget</span>
                  <span className="text-lg font-semibold text-green-600">
                    ${(department.budget / 1000).toLocaleString()}K
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredDepartments.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No departments found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {searchTerm || filterStatus !== 'all' 
              ? 'Try adjusting your search criteria'
              : 'Get started by creating your first department'
            }
          </p>
          {!searchTerm && filterStatus === 'all' && (
            <button className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
              <Plus className="h-4 w-4 mr-2" />
              Add Department
            </button>
          )}
        </div>
      )}
    </div>
  );
}
