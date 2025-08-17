import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  Calculator, 
  Receipt, 
  Calendar, 
  Plus,
  Download,
  Eye,
  Edit3,
  Filter,
  Search,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Users,
  FileText,
  CreditCard,
  Percent
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface PayrollEntry {
  id: string;
  employeeId: string;
  employeeName: string;
  position: string;
  department: string;
  payPeriod: {
    start: string;
    end: string;
  };
  basicSalary: number;
  allowances: {
    housing: number;
    transport: number;
    meal: number;
    other: number;
  };
  deductions: {
    tax: number;
    insurance: number;
    pension: number;
    loan: number;
    other: number;
  };
  overtime: {
    hours: number;
    rate: number;
    amount: number;
  };
  bonus: number;
  grossPay: number;
  totalDeductions: number;
  netPay: number;
  status: 'draft' | 'calculated' | 'approved' | 'paid';
  processedBy: string;
  processedDate: string;
  paymentMethod: 'bank-transfer' | 'check' | 'cash';
  bankDetails?: {
    bankName: string;
    accountNumber: string;
  };
}

interface PayrollSummary {
  totalEmployees: number;
  totalGrossPay: number;
  totalDeductions: number;
  totalNetPay: number;
  averageSalary: number;
  payrollByDepartment: {
    department: string;
    employees: number;
    totalPay: number;
    avgPay: number;
  }[];
}

const mockPayrollEntries: PayrollEntry[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'John Doe',
    position: 'Senior Software Engineer',
    department: 'Engineering',
    payPeriod: {
      start: '2024-08-01',
      end: '2024-08-31'
    },
    basicSalary: 8000,
    allowances: {
      housing: 2000,
      transport: 500,
      meal: 300,
      other: 200
    },
    deductions: {
      tax: 1200,
      insurance: 400,
      pension: 800,
      loan: 0,
      other: 0
    },
    overtime: {
      hours: 10,
      rate: 50,
      amount: 500
    },
    bonus: 1000,
    grossPay: 12500,
    totalDeductions: 2400,
    netPay: 10100,
    status: 'paid',
    processedBy: 'HR Manager',
    processedDate: '2024-08-28',
    paymentMethod: 'bank-transfer',
    bankDetails: {
      bankName: 'National Bank',
      accountNumber: '****1234'
    }
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Sarah Williams',
    position: 'Product Manager',
    department: 'Product',
    payPeriod: {
      start: '2024-08-01',
      end: '2024-08-31'
    },
    basicSalary: 7500,
    allowances: {
      housing: 1800,
      transport: 500,
      meal: 300,
      other: 200
    },
    deductions: {
      tax: 1125,
      insurance: 375,
      pension: 750,
      loan: 200,
      other: 0
    },
    overtime: {
      hours: 0,
      rate: 0,
      amount: 0
    },
    bonus: 500,
    grossPay: 10800,
    totalDeductions: 2450,
    netPay: 8350,
    status: 'approved',
    processedBy: 'HR Manager',
    processedDate: '2024-08-25',
    paymentMethod: 'bank-transfer',
    bankDetails: {
      bankName: 'City Bank',
      accountNumber: '****5678'
    }
  },
  {
    id: '3',
    employeeId: 'EMP003',
    employeeName: 'Mike Johnson',
    position: 'Sales Representative',
    department: 'Sales',
    payPeriod: {
      start: '2024-08-01',
      end: '2024-08-31'
    },
    basicSalary: 5000,
    allowances: {
      housing: 1200,
      transport: 600,
      meal: 300,
      other: 400
    },
    deductions: {
      tax: 750,
      insurance: 250,
      pension: 500,
      loan: 150,
      other: 0
    },
    overtime: {
      hours: 5,
      rate: 25,
      amount: 125
    },
    bonus: 2000,
    grossPay: 9625,
    totalDeductions: 1650,
    netPay: 7975,
    status: 'calculated',
    processedBy: 'HR Assistant',
    processedDate: '2024-08-20',
    paymentMethod: 'bank-transfer'
  }
];

const mockPayrollSummary: PayrollSummary = {
  totalEmployees: 45,
  totalGrossPay: 425000,
  totalDeductions: 95000,
  totalNetPay: 330000,
  averageSalary: 7333,
  payrollByDepartment: [
    { department: 'Engineering', employees: 15, totalPay: 150000, avgPay: 10000 },
    { department: 'Sales', employees: 12, totalPay: 96000, avgPay: 8000 },
    { department: 'Product', employees: 8, totalPay: 72000, avgPay: 9000 },
    { department: 'Marketing', employees: 6, totalPay: 42000, avgPay: 7000 },
    { department: 'HR', employees: 4, totalPay: 28000, avgPay: 7000 }
  ]
};

export default function PayrollManagement() {
  const [payrollEntries, setPayrollEntries] = useState<PayrollEntry[]>([]);
  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'draft' | 'calculated' | 'approved' | 'paid'>('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'payroll' | 'summary' | 'reports'>('payroll');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setPayrollEntries(mockPayrollEntries);
      setSummary(mockPayrollSummary);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredEntries = payrollEntries.filter(entry => {
    const matchesSearch = entry.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      entry.department.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || entry.status === statusFilter;
    const matchesDepartment = departmentFilter === 'all' || entry.department === departmentFilter;
    
    return matchesSearch && matchesStatus && matchesDepartment;
  });

  const departments = ['all', ...Array.from(new Set(payrollEntries.map(entry => entry.department)))];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'approved':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'calculated':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'draft':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid':
        return <CheckCircle className="h-4 w-4" />;
      case 'approved':
        return <CheckCircle className="h-4 w-4" />;
      case 'calculated':
        return <Calculator className="h-4 w-4" />;
      case 'draft':
        return <Clock className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
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
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-xl">
              <DollarSign className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            Payroll Management
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Manage employee payroll, salaries, and compensation
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
            <Download className="h-4 w-4" />
            Export Payroll
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
            <Plus className="h-4 w-4" />
            Process Payroll
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Employees</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{summary.totalEmployees}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Gross Pay</p>
                <p className="text-3xl font-bold text-green-600">{formatCurrency(summary.totalGrossPay)}</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Deductions</p>
                <p className="text-3xl font-bold text-red-600">{formatCurrency(summary.totalDeductions)}</p>
              </div>
              <div className="p-3 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <Receipt className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Net Pay</p>
                <p className="text-3xl font-bold text-blue-600">{formatCurrency(summary.totalNetPay)}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <CreditCard className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { key: 'payroll', label: 'Payroll Entries', icon: DollarSign },
            { key: 'summary', label: 'Department Summary', icon: Calculator },
            { key: 'reports', label: 'Payroll Reports', icon: FileText }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-green-500 text-green-600 dark:text-green-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="p-6">
          {/* Payroll Tab */}
          {activeTab === 'payroll' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    type="text"
                    placeholder="Search employees..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Status</option>
                  <option value="paid">Paid</option>
                  <option value="approved">Approved</option>
                  <option value="calculated">Calculated</option>
                  <option value="draft">Draft</option>
                </select>
                <select
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  {departments.map(dept => (
                    <option key={dept} value={dept}>
                      {dept === 'all' ? 'All Departments' : dept}
                    </option>
                  ))}
                </select>
              </div>

              {/* Payroll Entries */}
              <div className="space-y-4">
                {filteredEntries.map((entry) => (
                  <div
                    key={entry.id}
                    className="border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {entry.employeeName}
                          </h3>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(entry.status)}
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(entry.status)}`}>
                              {entry.status.toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mb-1">{entry.position} • {entry.department}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          Pay Period: {new Date(entry.payPeriod.start).toLocaleDateString()} - {new Date(entry.payPeriod.end).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-sm text-gray-500 dark:text-gray-500">Net Pay</p>
                          <p className="text-2xl font-bold text-green-600">{formatCurrency(entry.netPay)}</p>
                        </div>
                        
                        <div className="flex gap-2">
                          <button className="p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/20 rounded-lg transition-colors">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300 hover:bg-green-100 dark:hover:bg-green-900/20 rounded-lg transition-colors">
                            <Edit3 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                      {/* Salary Breakdown */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Salary Components</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Basic Salary</span>
                            <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(entry.basicSalary)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Allowances</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {formatCurrency(Object.values(entry.allowances).reduce((sum, val) => sum + val, 0))}
                            </span>
                          </div>
                          {entry.overtime.amount > 0 && (
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">Overtime</span>
                              <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(entry.overtime.amount)}</span>
                            </div>
                          )}
                          {entry.bonus > 0 && (
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">Bonus</span>
                              <span className="font-medium text-green-600">{formatCurrency(entry.bonus)}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Allowances */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Allowances</h4>
                        <div className="space-y-2 text-sm">
                          {Object.entries(entry.allowances).map(([key, value]) => (
                            value > 0 && (
                              <div key={key} className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400 capitalize">{key}</span>
                                <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(value)}</span>
                              </div>
                            )
                          ))}
                        </div>
                      </div>

                      {/* Deductions */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Deductions</h4>
                        <div className="space-y-2 text-sm">
                          {Object.entries(entry.deductions).map(([key, value]) => (
                            value > 0 && (
                              <div key={key} className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400 capitalize">{key}</span>
                                <span className="font-medium text-red-600">-{formatCurrency(value)}</span>
                              </div>
                            )
                          ))}
                        </div>
                      </div>

                      {/* Payment Details */}
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Payment Info</h4>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Gross Pay</span>
                            <span className="font-medium text-gray-900 dark:text-white">{formatCurrency(entry.grossPay)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Deductions</span>
                            <span className="font-medium text-red-600">-{formatCurrency(entry.totalDeductions)}</span>
                          </div>
                          <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-600">
                            <span className="font-semibold text-gray-900 dark:text-white">Net Pay</span>
                            <span className="font-bold text-green-600">{formatCurrency(entry.netPay)}</span>
                          </div>
                          {entry.paymentMethod && (
                            <p className="text-xs text-gray-500 dark:text-gray-500 pt-2">
                              Payment: {entry.paymentMethod.replace('-', ' ').toUpperCase()}
                              {entry.bankDetails && ` • ${entry.bankDetails.bankName} ${entry.bankDetails.accountNumber}`}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary Tab */}
          {activeTab === 'summary' && summary && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Department Breakdown */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payroll by Department</h3>
                  <div className="space-y-4">
                    {summary.payrollByDepartment.map((dept, index) => (
                      <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900 dark:text-white">{dept.department}</h4>
                          <span className="text-sm text-gray-600 dark:text-gray-400">{dept.employees} employees</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">Total Pay</p>
                            <p className="text-xl font-bold text-green-600">{formatCurrency(dept.totalPay)}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600 dark:text-gray-400">Avg Pay</p>
                            <p className="text-lg font-semibold text-gray-900 dark:text-white">{formatCurrency(dept.avgPay)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Payment Stats */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payment Statistics</h3>
                  <div className="space-y-4">
                    <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Salary</p>
                          <p className="text-2xl font-bold text-gray-900 dark:text-white">{formatCurrency(summary.averageSalary)}</p>
                        </div>
                        <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                          <Calculator className="h-6 w-6 text-green-600 dark:text-green-400" />
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Payroll Efficiency</p>
                        <div className="flex items-center justify-center gap-1 mt-1">
                          <Percent className="h-4 w-4 text-green-600" />
                          <span className="text-lg font-bold text-green-600">77.6%</span>
                        </div>
                      </div>
                      <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-center">
                        <p className="text-sm text-gray-600 dark:text-gray-400">On-time Payments</p>
                        <div className="flex items-center justify-center gap-1 mt-1">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          <span className="text-lg font-bold text-green-600">98%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
