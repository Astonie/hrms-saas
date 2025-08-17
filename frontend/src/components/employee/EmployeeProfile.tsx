import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar, 
  Building2,
  Briefcase,
  DollarSign,
  GraduationCap,
  Award,
  Clock,
  Edit3,
  Save,
  X,
  Plus,
  Trash2,
  FileText,
  Camera,
  Globe,
  LinkedinIcon,
  Twitter,
  Target
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface EmployeeDetail {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  position: string;
  department: string;
  manager: string;
  hireDate: string;
  salary: number;
  status: 'active' | 'inactive' | 'on-leave' | 'terminated';
  avatar?: string;
  
  // Personal Information
  dateOfBirth: string;
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  };
  
  // Professional Information
  employeeId: string;
  workLocation: string;
  employmentType: 'full-time' | 'part-time' | 'contract' | 'intern';
  reportingManager: string;
  team: string;
  level: string;
  
  // Skills & Education
  skills: string[];
  education: {
    degree: string;
    institution: string;
    year: number;
  }[];
  certifications: {
    name: string;
    issuer: string;
    date: string;
    expiry?: string;
  }[];
  
  // Performance & Goals
  performanceRating: number;
  goals: {
    title: string;
    description: string;
    progress: number;
    deadline: string;
    status: 'not-started' | 'in-progress' | 'completed' | 'overdue';
  }[];
  
  // Social Links
  socialLinks: {
    linkedin?: string;
    twitter?: string;
    website?: string;
  };
  
  // System Information
  lastLogin: string;
  createdAt: string;
  updatedAt: string;
}

const mockEmployeeDetail: EmployeeDetail = {
  id: 1,
  firstName: 'John',
  lastName: 'Doe',
  email: 'john.doe@company.com',
  phone: '+1 (555) 123-4567',
  position: 'Senior Software Engineer',
  department: 'Engineering',
  manager: 'Sarah Johnson',
  hireDate: '2023-01-15',
  salary: 95000,
  status: 'active',
  
  dateOfBirth: '1990-05-15',
  address: {
    street: '123 Tech Street',
    city: 'San Francisco',
    state: 'CA',
    zipCode: '94107',
    country: 'USA'
  },
  emergencyContact: {
    name: 'Jane Doe',
    phone: '+1 (555) 987-6543',
    relationship: 'Spouse'
  },
  
  employeeId: 'ENG001',
  workLocation: 'San Francisco HQ',
  employmentType: 'full-time',
  reportingManager: 'Sarah Johnson',
  team: 'Platform Engineering',
  level: 'Senior',
  
  skills: ['React', 'TypeScript', 'Node.js', 'Python', 'AWS', 'Docker', 'Kubernetes'],
  education: [
    {
      degree: 'Master of Science in Computer Science',
      institution: 'Stanford University',
      year: 2018
    },
    {
      degree: 'Bachelor of Science in Software Engineering',
      institution: 'UC Berkeley',
      year: 2016
    }
  ],
  certifications: [
    {
      name: 'AWS Solutions Architect Professional',
      issuer: 'Amazon Web Services',
      date: '2024-03-15',
      expiry: '2027-03-15'
    },
    {
      name: 'Kubernetes Certified Administrator',
      issuer: 'CNCF',
      date: '2023-08-20',
      expiry: '2026-08-20'
    }
  ],
  
  performanceRating: 4.5,
  goals: [
    {
      title: 'Lead Platform Modernization',
      description: 'Migrate legacy systems to cloud-native architecture',
      progress: 75,
      deadline: '2024-12-31',
      status: 'in-progress'
    },
    {
      title: 'Mentor Junior Developers',
      description: 'Guide 3 junior developers in their career growth',
      progress: 90,
      deadline: '2024-10-30',
      status: 'in-progress'
    }
  ],
  
  socialLinks: {
    linkedin: 'https://linkedin.com/in/johndoe',
    twitter: 'https://twitter.com/johndoe',
    website: 'https://johndoe.dev'
  },
  
  lastLogin: '2024-08-17T09:30:00Z',
  createdAt: '2023-01-15T10:00:00Z',
  updatedAt: '2024-08-16T15:45:00Z'
};

export default function EmployeeProfile({ employeeId }: { employeeId?: string }) {
  const [employee, setEmployee] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'personal' | 'professional' | 'skills' | 'performance' | 'goals'>('overview');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setEmployee(mockEmployeeDetail);
      setLoading(false);
    }, 1000);
  }, [employeeId]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'inactive':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      case 'on-leave':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'terminated':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-blue-500';
    if (progress >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!employee) {
    return <div>Employee not found</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 h-32"></div>
        <div className="px-6 pb-6">
          <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between -mt-16">
            <div className="flex items-end gap-4">
              <div className="h-24 w-24 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold border-4 border-white dark:border-gray-800 shadow-lg">
                {employee.avatar ? (
                  <img src={employee.avatar} alt={`${employee.firstName} ${employee.lastName}`} className="h-full w-full rounded-full object-cover" />
                ) : (
                  getInitials(employee.firstName, employee.lastName)
                )}
              </div>
              <div className="pb-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {employee.firstName} {employee.lastName}
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400">{employee.position}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getStatusBadge(employee.status)}`}>
                    {employee.status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    ID: {employee.employeeId}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-4 sm:mt-0">
              <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                <Mail className="h-4 w-4" />
                Message
              </button>
              <button 
                onClick={() => setIsEditing(!isEditing)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                {isEditing ? <X className="h-4 w-4" /> : <Edit3 className="h-4 w-4" />}
                {isEditing ? 'Cancel' : 'Edit'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Years at Company</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {Math.floor((new Date().getTime() - new Date(employee.hireDate).getTime()) / (365.25 * 24 * 60 * 60 * 1000))}
              </p>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Calendar className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Performance</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{employee.performanceRating}/5</p>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Award className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Goals</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {employee.goals.filter(g => g.status === 'in-progress').length}
              </p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Target className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Skills</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{employee.skills.length}</p>
            </div>
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
              <GraduationCap className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { key: 'overview', label: 'Overview', icon: User },
            { key: 'personal', label: 'Personal', icon: MapPin },
            { key: 'professional', label: 'Professional', icon: Briefcase },
            { key: 'skills', label: 'Skills & Education', icon: GraduationCap },
            { key: 'performance', label: 'Performance', icon: Award },
            { key: 'goals', label: 'Goals', icon: Target }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
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
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Contact Information</h3>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <Mail className="h-5 w-5 text-gray-400" />
                      <span className="text-gray-900 dark:text-white">{employee.email}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Phone className="h-5 w-5 text-gray-400" />
                      <span className="text-gray-900 dark:text-white">{employee.phone}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Building2 className="h-5 w-5 text-gray-400" />
                      <span className="text-gray-900 dark:text-white">{employee.department}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <MapPin className="h-5 w-5 text-gray-400" />
                      <span className="text-gray-900 dark:text-white">{employee.workLocation}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Social Links</h3>
                  <div className="flex gap-3">
                    {employee.socialLinks.linkedin && (
                      <a href={employee.socialLinks.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/30 transition-colors">
                        <LinkedinIcon className="h-5 w-5" />
                      </a>
                    )}
                    {employee.socialLinks.twitter && (
                      <a href={employee.socialLinks.twitter} target="_blank" rel="noopener noreferrer" className="p-2 bg-blue-100 dark:bg-blue-900/20 text-blue-400 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/30 transition-colors">
                        <Twitter className="h-5 w-5" />
                      </a>
                    )}
                    {employee.socialLinks.website && (
                      <a href={employee.socialLinks.website} target="_blank" rel="noopener noreferrer" className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
                        <Globe className="h-5 w-5" />
                      </a>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Employment Details</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Employee ID:</span>
                      <span className="text-gray-900 dark:text-white font-medium">{employee.employeeId}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Hire Date:</span>
                      <span className="text-gray-900 dark:text-white font-medium">
                        {new Date(employee.hireDate).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Employment Type:</span>
                      <span className="text-gray-900 dark:text-white font-medium capitalize">
                        {employee.employmentType.replace('-', ' ')}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Manager:</span>
                      <span className="text-gray-900 dark:text-white font-medium">{employee.reportingManager}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Team:</span>
                      <span className="text-gray-900 dark:text-white font-medium">{employee.team}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Level:</span>
                      <span className="text-gray-900 dark:text-white font-medium">{employee.level}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                      <Clock className="h-4 w-4" />
                      Last login: {new Date(employee.lastLogin).toLocaleString()}
                    </div>
                    <div className="flex items-center gap-3 text-gray-600 dark:text-gray-400">
                      <Calendar className="h-4 w-4" />
                      Profile updated: {new Date(employee.updatedAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Goals Tab */}
          {activeTab === 'goals' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Current Goals</h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Plus className="h-4 w-4" />
                  Add Goal
                </button>
              </div>
              <div className="space-y-4">
                {employee.goals.map((goal, index) => (
                  <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-900 dark:text-white">{goal.title}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{goal.description}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        goal.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                        goal.status === 'in-progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400' :
                        goal.status === 'overdue' ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
                      }`}>
                        {goal.status.replace('-', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Progress</span>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">{goal.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
                      <div 
                        className={`h-2 rounded-full transition-all ${getProgressColor(goal.progress)}`}
                        style={{ width: `${goal.progress}%` }}
                      ></div>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        Due: {new Date(goal.deadline).toLocaleDateString()}
                      </span>
                      <div className="flex gap-2">
                        <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Add more tabs content here... */}
        </div>
      </div>
    </div>
  );
}
