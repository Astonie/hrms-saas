import React, { Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'

// Lazy load components for better performance
const Login = React.lazy(() => import('./pages/auth/Login'))
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'))
const Layout = React.lazy(() => import('./components/layout/Layout'))
const LoadingSpinner = React.lazy(() => import('./components/ui/LoadingSpinner'))

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Public Route Component (redirects if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            
            {/* Employee Management */}
            <Route path="employees">
              <Route index element={<div>Employees List</div>} />
              <Route path="new" element={<div>New Employee</div>} />
              <Route path=":id" element={<div>Employee Details</div>} />
              <Route path=":id/edit" element={<div>Edit Employee</div>} />
            </Route>

            {/* Department Management */}
            <Route path="departments">
              <Route index element={<div>Departments List</div>} />
              <Route path="new" element={<div>New Department</div>} />
              <Route path=":id" element={<div>Department Details</div>} />
              <Route path=":id/edit" element={<div>Edit Department</div>} />
            </Route>

            {/* Leave Management */}
            <Route path="leave">
              <Route index element={<div>Leave Requests</div>} />
              <Route path="new" element={<div>New Leave Request</div>} />
              <Route path=":id" element={<div>Leave Request Details</div>} />
              <Route path="calendar" element={<div>Leave Calendar</div>} />
            </Route>

            {/* Payroll Management */}
            <Route path="payroll">
              <Route index element={<div>Payroll Overview</div>} />
              <Route path="employees" element={<div>Employee Payroll</div>} />
              <Route path="reports" element={<div>Payroll Reports</div>} />
            </Route>

            {/* Performance Management */}
            <Route path="performance">
              <Route index element={<div>Performance Overview</div>} />
              <Route path="reviews" element={<div>Performance Reviews</div>} />
              <Route path="goals" element={<div>Goals & Objectives</div>} />
            </Route>

            {/* Recruitment Management */}
            <Route path="recruitment">
              <Route index element={<div>Recruitment Overview</div>} />
              <Route path="jobs" element={<div>Job Postings</div>} />
              <Route path="candidates" element={<div>Candidates</div>} />
              <Route path="interviews" element={<div>Interviews</div>} />
            </Route>

            {/* Attendance Management */}
            <Route path="attendance">
              <Route index element={<div>Attendance Overview</div>} />
              <Route path="time-tracking" element={<div>Time Tracking</div>} />
              <Route path="reports" element={<div>Attendance Reports</div>} />
            </Route>

            {/* Document Management */}
            <Route path="documents">
              <Route index element={<div>Documents</div>} />
              <Route path="upload" element={<div>Upload Document</div>} />
              <Route path=":id" element={<div>Document Details</div>} />
            </Route>

            {/* User Management */}
            <Route path="users">
              <Route index element={<div>Users List</div>} />
              <Route path="new" element={<div>New User</div>} />
              <Route path=":id" element={<div>User Details</div>} />
              <Route path=":id/edit" element={<div>Edit User</div>} />
            </Route>

            {/* Settings */}
            <Route path="settings">
              <Route index element={<div>General Settings</div>} />
              <Route path="profile" element={<div>Profile Settings</div>} />
              <Route path="security" element={<div>Security Settings</div>} />
              <Route path="notifications" element={<div>Notification Settings</div>} />
            </Route>

            {/* Catch all route */}
            <Route path="*" element={<div>Page Not Found</div>} />
          </Route>
        </Routes>
      </Suspense>
    </div>
  )
}

export default App
