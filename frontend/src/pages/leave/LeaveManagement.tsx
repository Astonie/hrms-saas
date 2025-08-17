import React, { useState } from 'react';
import { 
  Calendar, 
  Plus, 
  Filter, 
  Search, 
  Clock, 
  Check, 
  X, 
  Eye,
  Edit,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle,
  XCircle,
  User,
  Building2
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useLeaveRequests, useMyLeaveRequests, useLeaveBalances, useCreateLeaveRequest } from '../../hooks/useApi';
import { useDepartments } from '../../hooks/useApi';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import type { LeaveRequest, LeaveRequestCreate } from '../../types';

interface LeaveRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: LeaveRequestCreate) => void;
  loading?: boolean;
}

const LeaveRequestModal: React.FC<LeaveRequestModalProps> = ({ isOpen, onClose, onSubmit, loading }) => {
  const [formData, setFormData] = useState<LeaveRequestCreate>({
    leave_type: 'ANNUAL',
    start_date: '',
    end_date: '',
    is_half_day: false,
    reason: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Request Leave</h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Leave Type
            </label>
            <select
              value={formData.leave_type}
              onChange={(e) => setFormData({ ...formData, leave_type: e.target.value as any })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              required
            >
              <option value="ANNUAL">Annual Leave</option>
              <option value="SICK">Sick Leave</option>
              <option value="PERSONAL">Personal Leave</option>
              <option value="MATERNITY">Maternity Leave</option>
              <option value="PATERNITY">Paternity Leave</option>
              <option value="BEREAVEMENT">Bereavement Leave</option>
              <option value="EMERGENCY">Emergency Leave</option>
              <option value="UNPAID">Unpaid Leave</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
          </div>

          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={formData.is_half_day}
                onChange={(e) => setFormData({ ...formData, is_half_day: e.target.checked })}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">Half Day Leave</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Reason
            </label>
            <textarea
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Please provide reason for leave..."
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Additional Notes (Optional)
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Any additional information..."
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {loading && <LoadingSpinner />}
              <span>Submit Request</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const LeaveCard: React.FC<{ request: LeaveRequest; onView?: () => void }> = ({ request, onView }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'REJECTED':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'PENDING':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <CheckCircle className="h-4 w-4" />;
      case 'REJECTED':
        return <XCircle className="h-4 w-4" />;
      case 'PENDING':
        return <Clock className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 dark:border-gray-700/50 p-6 hover:shadow-lg transition-all duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
            {request.leave_type.replace('_', ' ')} Leave
          </h3>
          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 space-x-4">
            <span className="flex items-center">
              <User className="h-4 w-4 mr-1" />
              {request.employee_name}
            </span>
            {request.department_name && (
              <span className="flex items-center">
                <Building2 className="h-4 w-4 mr-1" />
                {request.department_name}
              </span>
            )}
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(request.status)}`}>
          {getStatusIcon(request.status)}
          <span>{request.status}</span>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Duration:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {new Date(request.start_date).toLocaleDateString()} - {new Date(request.end_date).toLocaleDateString()}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Days:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {request.requested_days} {request.is_half_day ? '(Half Day)' : ''}
          </span>
        </div>
        <div className="flex items-start justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Reason:</span>
          <span className="font-medium text-gray-900 dark:text-white text-right ml-2 line-clamp-2">
            {request.reason}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Requested {new Date(request.created_at).toLocaleDateString()}
        </span>
        <button
          onClick={onView}
          className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 dark:text-blue-400 text-sm font-medium"
        >
          <Eye className="h-4 w-4" />
          <span>View Details</span>
        </button>
      </div>
    </div>
  );
};

export default function LeaveManagement() {
  const { user, hasPermission } = useAuth();
  const [activeTab, setActiveTab] = useState<'my-requests' | 'all-requests' | 'balances'>('my-requests');
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    leave_type: '',
    department_id: ''
  });

  // Hooks for data fetching
  const myLeaveRequests = useMyLeaveRequests({
    search: filters.search || undefined,
    status: filters.status || undefined,
    leave_type: filters.leave_type || undefined
  });
  
  const allLeaveRequests = useLeaveRequests({
    search: filters.search || undefined,
    status: filters.status || undefined,
    leave_type: filters.leave_type || undefined,
    department_id: filters.department_id || undefined
  });

  const { balances, loading: balancesLoading } = useLeaveBalances();
  const { departments } = useDepartments();
  const { mutate: createLeaveRequest, loading: creating } = useCreateLeaveRequest(() => {
    setShowRequestModal(false);
    myLeaveRequests.refresh();
    if (hasPermission('leave:view_all')) {
      allLeaveRequests.refresh();
    }
  });

  const canViewAll = hasPermission('leave:view_all');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Leave Management</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Manage leave requests and track balances
          </p>
        </div>
        <button
          onClick={() => setShowRequestModal(true)}
          className="mt-4 sm:mt-0 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-lg"
        >
          <Plus className="h-5 w-5" />
          <span>Request Leave</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('my-requests')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'my-requests'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            My Requests
          </button>
          {canViewAll && (
            <button
              onClick={() => setActiveTab('all-requests')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'all-requests'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              All Requests
            </button>
          )}
          <button
            onClick={() => setActiveTab('balances')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'balances'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Leave Balances
          </button>
        </nav>
      </div>

      {/* Filters */}
      {(activeTab === 'my-requests' || activeTab === 'all-requests') && (
        <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 dark:border-gray-700/50 p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search requests..."
                  value={filters.search}
                  onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Statuses</option>
                <option value="PENDING">Pending</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Leave Type
              </label>
              <select
                value={filters.leave_type}
                onChange={(e) => setFilters({ ...filters, leave_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Types</option>
                <option value="ANNUAL">Annual Leave</option>
                <option value="SICK">Sick Leave</option>
                <option value="PERSONAL">Personal Leave</option>
                <option value="MATERNITY">Maternity Leave</option>
                <option value="PATERNITY">Paternity Leave</option>
                <option value="BEREAVEMENT">Bereavement Leave</option>
                <option value="EMERGENCY">Emergency Leave</option>
                <option value="UNPAID">Unpaid Leave</option>
              </select>
            </div>
            {activeTab === 'all-requests' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Department
                </label>
                <select
                  value={filters.department_id}
                  onChange={(e) => setFilters({ ...filters, department_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">All Departments</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      {activeTab === 'my-requests' && (
        <div>
          {myLeaveRequests.loading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner />
            </div>
          ) : myLeaveRequests.error ? (
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">{myLeaveRequests.error}</p>
            </div>
          ) : myLeaveRequests.data.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No leave requests</h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">You haven't submitted any leave requests yet.</p>
              <button
                onClick={() => setShowRequestModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Request Leave
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {myLeaveRequests.data.map((request) => (
                <LeaveCard key={request.id} request={request} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'all-requests' && canViewAll && (
        <div>
          {allLeaveRequests.loading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner />
            </div>
          ) : allLeaveRequests.error ? (
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400">{allLeaveRequests.error}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {allLeaveRequests.data.map((request) => (
                <LeaveCard key={request.id} request={request} />
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'balances' && (
        <div>
          {balancesLoading ? (
            <div className="flex items-center justify-center h-64">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {balances.map((balance) => (
                <div key={balance.id} className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 dark:border-gray-700/50 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    {balance.leave_type.replace('_', ' ')} Leave
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Total Days:</span>
                      <span className="font-medium text-gray-900 dark:text-white">{balance.total_days}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Used:</span>
                      <span className="font-medium text-red-600 dark:text-red-400">{balance.used_days}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Pending:</span>
                      <span className="font-medium text-yellow-600 dark:text-yellow-400">{balance.pending_days}</span>
                    </div>
                    <div className="flex justify-between border-t border-gray-200 dark:border-gray-700 pt-3">
                      <span className="font-medium text-gray-900 dark:text-white">Remaining:</span>
                      <span className="font-bold text-green-600 dark:text-green-400">{balance.remaining_days}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Request Leave Modal */}
      <LeaveRequestModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        onSubmit={createLeaveRequest}
        loading={creating}
      />
    </div>
  );
}
