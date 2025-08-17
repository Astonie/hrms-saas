import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Search, 
  Filter, 
  Expand, 
  Minimize, 
  Eye, 
  Mail,
  Phone,
  Building2,
  ChevronDown,
  ChevronRight,
  UserPlus,
  Edit3,
  MoreVertical
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface OrgEmployee {
  id: string;
  name: string;
  position: string;
  department: string;
  email: string;
  phone?: string;
  avatar?: string;
  managerId?: string;
  level: number;
  children: OrgEmployee[];
  isExpanded: boolean;
}

const mockOrgData: OrgEmployee = {
  id: '1',
  name: 'John Smith',
  position: 'Chief Executive Officer',
  department: 'Executive',
  email: 'john.smith@company.com',
  phone: '+1 (555) 100-0001',
  level: 0,
  children: [
    {
      id: '2',
      name: 'Sarah Johnson',
      position: 'VP of Engineering',
      department: 'Engineering',
      email: 'sarah.johnson@company.com',
      phone: '+1 (555) 100-0002',
      managerId: '1',
      level: 1,
      isExpanded: true,
      children: [
        {
          id: '3',
          name: 'Michael Chen',
          position: 'Senior Engineering Manager',
          department: 'Engineering',
          email: 'michael.chen@company.com',
          managerId: '2',
          level: 2,
          isExpanded: true,
          children: [
            {
              id: '4',
              name: 'Emily Davis',
              position: 'Senior Software Engineer',
              department: 'Engineering',
              email: 'emily.davis@company.com',
              managerId: '3',
              level: 3,
              isExpanded: false,
              children: []
            },
            {
              id: '5',
              name: 'David Wilson',
              position: 'Software Engineer',
              department: 'Engineering',
              email: 'david.wilson@company.com',
              managerId: '3',
              level: 3,
              isExpanded: false,
              children: []
            }
          ]
        },
        {
          id: '6',
          name: 'Lisa Rodriguez',
          position: 'DevOps Manager',
          department: 'Engineering',
          email: 'lisa.rodriguez@company.com',
          managerId: '2',
          level: 2,
          isExpanded: false,
          children: [
            {
              id: '7',
              name: 'Tom Anderson',
              position: 'DevOps Engineer',
              department: 'Engineering',
              email: 'tom.anderson@company.com',
              managerId: '6',
              level: 3,
              isExpanded: false,
              children: []
            }
          ]
        }
      ]
    },
    {
      id: '8',
      name: 'Robert Taylor',
      position: 'VP of Sales',
      department: 'Sales',
      email: 'robert.taylor@company.com',
      phone: '+1 (555) 100-0008',
      managerId: '1',
      level: 1,
      isExpanded: true,
      children: [
        {
          id: '9',
          name: 'Jennifer Lee',
          position: 'Sales Manager',
          department: 'Sales',
          email: 'jennifer.lee@company.com',
          managerId: '8',
          level: 2,
          isExpanded: false,
          children: [
            {
              id: '10',
              name: 'Kevin Martinez',
              position: 'Account Executive',
              department: 'Sales',
              email: 'kevin.martinez@company.com',
              managerId: '9',
              level: 3,
              isExpanded: false,
              children: []
            },
            {
              id: '11',
              name: 'Amanda Brown',
              position: 'Sales Representative',
              department: 'Sales',
              email: 'amanda.brown@company.com',
              managerId: '9',
              level: 3,
              isExpanded: false,
              children: []
            }
          ]
        }
      ]
    },
    {
      id: '12',
      name: 'Patricia Garcia',
      position: 'VP of Human Resources',
      department: 'Human Resources',
      email: 'patricia.garcia@company.com',
      phone: '+1 (555) 100-0012',
      managerId: '1',
      level: 1,
      isExpanded: false,
      children: [
        {
          id: '13',
          name: 'Mark Thompson',
          position: 'HR Manager',
          department: 'Human Resources',
          email: 'mark.thompson@company.com',
          managerId: '12',
          level: 2,
          isExpanded: false,
          children: []
        }
      ]
    }
  ],
  isExpanded: true
};

export default function OrganizationalChart() {
  const [orgData, setOrgData] = useState<OrgEmployee | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'tree' | 'list'>('tree');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setOrgData(mockOrgData);
      setLoading(false);
    }, 1000);
  }, []);

  const toggleExpand = (employeeId: string) => {
    if (!orgData) return;
    
    const updateNode = (node: OrgEmployee): OrgEmployee => {
      if (node.id === employeeId) {
        return { ...node, isExpanded: !node.isExpanded };
      }
      return {
        ...node,
        children: node.children.map(updateNode)
      };
    };

    setOrgData(updateNode(orgData));
  };

  const expandAll = () => {
    if (!orgData) return;
    
    const expandNode = (node: OrgEmployee): OrgEmployee => ({
      ...node,
      isExpanded: true,
      children: node.children.map(expandNode)
    });

    setOrgData(expandNode(orgData));
  };

  const collapseAll = () => {
    if (!orgData) return;
    
    const collapseNode = (node: OrgEmployee): OrgEmployee => ({
      ...node,
      isExpanded: node.level === 0, // Keep root expanded
      children: node.children.map(collapseNode)
    });

    setOrgData(collapseNode(orgData));
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const getDepartmentColor = (department: string) => {
    const colors: { [key: string]: string } = {
      'Executive': 'from-purple-500 to-indigo-600',
      'Engineering': 'from-blue-500 to-cyan-600',
      'Sales': 'from-green-500 to-emerald-600',
      'Human Resources': 'from-pink-500 to-rose-600',
      'Marketing': 'from-yellow-500 to-orange-600',
      'Finance': 'from-gray-500 to-slate-600'
    };
    return colors[department] || 'from-gray-400 to-gray-600';
  };

  const flattenOrgData = (node: OrgEmployee, result: OrgEmployee[] = []): OrgEmployee[] => {
    result.push(node);
    node.children.forEach(child => flattenOrgData(child, result));
    return result;
  };

  const filteredEmployees = orgData ? flattenOrgData(orgData).filter(emp =>
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.department.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const renderEmployeeCard = (employee: OrgEmployee, isCompact = false) => (
    <div
      key={employee.id}
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all cursor-pointer ${
        selectedEmployee === employee.id ? 'ring-2 ring-blue-500' : ''
      } ${isCompact ? 'p-3' : 'p-4'}`}
      onClick={() => setSelectedEmployee(selectedEmployee === employee.id ? null : employee.id)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`${isCompact ? 'h-10 w-10' : 'h-12 w-12'} rounded-full bg-gradient-to-r ${getDepartmentColor(employee.department)} flex items-center justify-center text-white font-semibold text-sm`}>
            {employee.avatar ? (
              <img src={employee.avatar} alt={employee.name} className="h-full w-full rounded-full object-cover" />
            ) : (
              getInitials(employee.name)
            )}
          </div>
          <div>
            <h4 className={`font-semibold text-gray-900 dark:text-white ${isCompact ? 'text-sm' : 'text-base'}`}>
              {employee.name}
            </h4>
            <p className={`text-gray-600 dark:text-gray-400 ${isCompact ? 'text-xs' : 'text-sm'}`}>
              {employee.position}
            </p>
            <p className={`text-gray-500 dark:text-gray-500 ${isCompact ? 'text-xs' : 'text-sm'}`}>
              {employee.department}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {employee.children.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleExpand(employee.id);
              }}
              className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              {employee.isExpanded ? (
                <ChevronDown className="h-4 w-4 text-gray-400" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-400" />
              )}
            </button>
          )}
          <div className="relative">
            <button className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
              <MoreVertical className="h-4 w-4 text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {selectedEmployee === employee.id && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
          <div className="grid grid-cols-1 gap-3">
            <div className="flex items-center gap-2 text-sm">
              <Mail className="h-4 w-4 text-gray-400" />
              <span className="text-gray-900 dark:text-white">{employee.email}</span>
            </div>
            {employee.phone && (
              <div className="flex items-center gap-2 text-sm">
                <Phone className="h-4 w-4 text-gray-400" />
                <span className="text-gray-900 dark:text-white">{employee.phone}</span>
              </div>
            )}
            {employee.children.length > 0 && (
              <div className="flex items-center gap-2 text-sm">
                <Users className="h-4 w-4 text-gray-400" />
                <span className="text-gray-900 dark:text-white">
                  {employee.children.length} direct report{employee.children.length !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
          <div className="flex gap-2 mt-4">
            <button className="flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-md text-sm hover:bg-blue-200 dark:hover:bg-blue-900/30">
              <Eye className="h-3 w-3" />
              View Profile
            </button>
            <button className="flex items-center gap-1 px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-sm hover:bg-gray-200 dark:hover:bg-gray-600">
              <Mail className="h-3 w-3" />
              Message
            </button>
            <button className="flex items-center gap-1 px-3 py-1 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-md text-sm hover:bg-green-200 dark:hover:bg-green-900/30">
              <Edit3 className="h-3 w-3" />
              Edit
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const renderOrgTree = (employee: OrgEmployee, isRoot = false) => (
    <div key={employee.id} className={`${!isRoot ? 'ml-8' : ''}`}>
      {renderEmployeeCard(employee)}
      
      {employee.isExpanded && employee.children.length > 0 && (
        <div className="mt-4 space-y-4 relative">
          {/* Connection lines */}
          {!isRoot && (
            <div className="absolute -left-4 top-0 bottom-0 w-px bg-gray-300 dark:bg-gray-600"></div>
          )}
          {employee.children.map((child, index) => (
            <div key={child.id} className="relative">
              {!isRoot && (
                <>
                  <div className="absolute -left-4 top-6 w-4 h-px bg-gray-300 dark:bg-gray-600"></div>
                  {index === employee.children.length - 1 && (
                    <div className="absolute -left-4 top-6 w-px h-full bg-white dark:bg-gray-900"></div>
                  )}
                </>
              )}
              {renderOrgTree(child)}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!orgData) {
    return <div>Error loading organizational chart</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-xl">
              <Users className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
            Organizational Chart
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Visualize your company's hierarchy and reporting structure
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <button
            onClick={() => setViewMode(viewMode === 'tree' ? 'list' : 'tree')}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Building2 className="h-4 w-4" />
            {viewMode === 'tree' ? 'List View' : 'Tree View'}
          </button>
          <button
            onClick={expandAll}
            className="flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/30 transition-colors"
          >
            <Expand className="h-4 w-4" />
            Expand All
          </button>
          <button
            onClick={collapseAll}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            <Minimize className="h-4 w-4" />
            Collapse All
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            placeholder="Search employees by name, position, or department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Employees</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{filteredEmployees.length}</p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Departments</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {new Set(filteredEmployees.map(e => e.department)).size}
              </p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Building2 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Management Levels</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {Math.max(...filteredEmployees.map(e => e.level)) + 1}
              </p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Expand className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Direct Reports</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {Math.max(...filteredEmployees.map(e => e.children.length))}
              </p>
            </div>
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
              <UserPlus className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Organizational Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        {searchTerm ? (
          // Search Results
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Search Results ({filteredEmployees.length})
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredEmployees.map(employee => renderEmployeeCard(employee, true))}
            </div>
          </div>
        ) : viewMode === 'tree' ? (
          // Tree View
          <div className="overflow-x-auto">
            <div className="min-w-full">
              {renderOrgTree(orgData, true)}
            </div>
          </div>
        ) : (
          // List View
          <div className="space-y-4">
            {filteredEmployees
              .sort((a, b) => a.level - b.level)
              .map(employee => (
                <div key={employee.id} className={`ml-${employee.level * 6}`}>
                  {renderEmployeeCard(employee, true)}
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
