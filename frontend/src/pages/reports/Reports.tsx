import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Download, 
  Filter, 
  Calendar,
  Users,
  Building2,
  DollarSign,
  Clock,
  FileText,
  BarChart3,
  PieChart,
  Target
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface ReportData {
  employeeStats: {
    total: number;
    active: number;
    inactive: number;
    newHires: number;
  };
  departmentStats: {
    total: number;
    averageSize: number;
    largest: string;
    budgetTotal: number;
  };
  leaveStats: {
    totalRequests: number;
    approved: number;
    pending: number;
    averageDays: number;
  };
  payrollStats: {
    totalPayroll: number;
    averageSalary: number;
    highestPaid: string;
    payrollGrowth: number;
  };
}

const mockReportData: ReportData = {
  employeeStats: {
    total: 156,
    active: 148,
    inactive: 8,
    newHires: 12
  },
  departmentStats: {
    total: 8,
    averageSize: 19.5,
    largest: 'Engineering',
    budgetTotal: 12500000
  },
  leaveStats: {
    totalRequests: 45,
    approved: 38,
    pending: 7,
    averageDays: 8.2
  },
  payrollStats: {
    totalPayroll: 18500000,
    averageSalary: 118590,
    highestPaid: 'Engineering',
    payrollGrowth: 12.5
  }
};

interface ChartData {
  departmentDistribution: { name: string; value: number; color: string }[];
  leaveTypeBreakdown: { name: string; value: number; color: string }[];
  monthlyHiring: { month: string; hires: number }[];
  salaryRanges: { range: string; count: number }[];
}

const mockChartData: ChartData = {
  departmentDistribution: [
    { name: 'Engineering', value: 35, color: '#3B82F6' },
    { name: 'Sales', value: 25, color: '#10B981' },
    { name: 'Marketing', value: 15, color: '#F59E0B' },
    { name: 'HR', value: 8, color: '#EF4444' },
    { name: 'Finance', value: 10, color: '#8B5CF6' },
    { name: 'Operations', value: 7, color: '#06B6D4' }
  ],
  leaveTypeBreakdown: [
    { name: 'Vacation', value: 45, color: '#3B82F6' },
    { name: 'Sick Leave', value: 25, color: '#EF4444' },
    { name: 'Personal', value: 20, color: '#F59E0B' },
    { name: 'Maternity', value: 10, color: '#EC4899' }
  ],
  monthlyHiring: [
    { month: 'Jan', hires: 8 },
    { month: 'Feb', hires: 12 },
    { month: 'Mar', hires: 15 },
    { month: 'Apr', hires: 10 },
    { month: 'May', hires: 18 },
    { month: 'Jun', hires: 22 },
    { month: 'Jul', hires: 16 },
    { month: 'Aug', hires: 20 }
  ],
  salaryRanges: [
    { range: '$40K-60K', count: 25 },
    { range: '$60K-80K', count: 45 },
    { range: '$80K-100K', count: 38 },
    { range: '$100K-120K', count: 28 },
    { range: '$120K+', count: 20 }
  ]
};

export default function Reports() {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'month' | 'quarter' | 'year'>('month');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setReportData(mockReportData);
      setChartData(mockChartData);
      setLoading(false);
    }, 1000);
  }, [selectedPeriod]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!reportData || !chartData) {
    return <div>Error loading report data</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <div className="p-2 bg-indigo-100 dark:bg-indigo-900/20 rounded-xl">
              <TrendingUp className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            Reports & Analytics
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Comprehensive insights into your HR metrics and trends
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as 'month' | 'quarter' | 'year')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
            <Download className="h-4 w-4" />
            Export Report
          </button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Employees</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{reportData.employeeStats.total}</p>
              <p className="text-sm text-green-600">+{reportData.employeeStats.newHires} new hires</p>
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
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{reportData.departmentStats.total}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Avg {reportData.departmentStats.averageSize} employees</p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Building2 className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Leave Requests</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{reportData.leaveStats.totalRequests}</p>
              <p className="text-sm text-yellow-600">{reportData.leaveStats.pending} pending</p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Calendar className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Payroll</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                ${(reportData.payrollStats.totalPayroll / 1000000).toFixed(1)}M
              </p>
              <p className="text-sm text-green-600">+{reportData.payrollStats.payrollGrowth}% growth</p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <DollarSign className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Department Distribution</h3>
            <PieChart className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {chartData.departmentDistribution.map((dept, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: dept.color }}
                  ></div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{dept.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{dept.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Leave Type Breakdown */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Leave Type Breakdown</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="space-y-4">
            {chartData.leaveTypeBreakdown.map((leave, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: leave.color }}
                  ></div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{leave.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900 dark:text-white">{leave.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Monthly Hiring Trend */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Monthly Hiring Trend</h3>
          <TrendingUp className="h-5 w-5 text-gray-400" />
        </div>
        <div className="grid grid-cols-8 gap-4">
          {chartData.monthlyHiring.map((month, index) => (
            <div key={index} className="text-center">
              <div className="flex flex-col items-center">
                <div 
                  className="w-8 bg-gradient-to-t from-indigo-500 to-indigo-300 rounded-t mb-2 transition-all hover:from-indigo-600 hover:to-indigo-400"
                  style={{ height: `${(month.hires / 25) * 100}px` }}
                ></div>
                <span className="text-sm font-medium text-gray-900 dark:text-white">{month.hires}</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">{month.month}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Salary Distribution */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Salary Distribution</h3>
          <DollarSign className="h-5 w-5 text-gray-400" />
        </div>
        <div className="space-y-4">
          {chartData.salaryRanges.map((range, index) => (
            <div key={index} className="flex items-center gap-4">
              <div className="w-20 text-sm text-gray-600 dark:text-gray-400">{range.range}</div>
              <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-green-500 to-emerald-400 h-2 rounded-full transition-all"
                  style={{ width: `${(range.count / 50) * 100}%` }}
                ></div>
              </div>
              <div className="w-12 text-sm font-medium text-gray-900 dark:text-white text-right">
                {range.count}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Metrics Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Target className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Employee Retention</h3>
          </div>
          <p className="text-3xl font-bold text-green-600 mb-2">94.8%</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Above industry average of 90%
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Clock className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Avg Time to Hire</h3>
          </div>
          <p className="text-3xl font-bold text-blue-600 mb-2">23 days</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            3 days faster than last quarter
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Training Completion</h3>
          </div>
          <p className="text-3xl font-bold text-purple-600 mb-2">87%</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            +12% from previous period
          </p>
        </div>
      </div>

      {/* Action Items */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recommended Actions</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Review pending leave requests
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {reportData.leaveStats.pending} requests awaiting approval
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Engineering team expansion
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Largest department may need resource planning
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Salary review cycle
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Quarterly compensation analysis due next month
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
