import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Award, 
  Target, 
  Calendar, 
  Plus,
  Eye,
  Edit3,
  Star,
  Clock,
  Users,
  BarChart3,
  PieChart,
  CheckCircle,
  AlertTriangle,
  Filter,
  Search,
  Download
} from 'lucide-react';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

interface PerformanceReview {
  id: string;
  employeeId: string;
  employeeName: string;
  position: string;
  department: string;
  reviewPeriod: {
    start: string;
    end: string;
  };
  status: 'draft' | 'in-progress' | 'completed' | 'overdue';
  overallRating: number;
  reviewerName: string;
  reviewDate: string;
  lastUpdated: string;
  categories: {
    name: string;
    score: number;
    weight: number;
    comments: string;
  }[];
  goals: {
    id: string;
    title: string;
    description: string;
    status: 'achieved' | 'partially-achieved' | 'not-achieved';
    rating: number;
  }[];
  strengths: string[];
  improvements: string[];
  nextPeriodGoals: string[];
}

const mockPerformanceReviews: PerformanceReview[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    employeeName: 'John Doe',
    position: 'Senior Software Engineer',
    department: 'Engineering',
    reviewPeriod: {
      start: '2024-01-01',
      end: '2024-06-30'
    },
    status: 'completed',
    overallRating: 4.3,
    reviewerName: 'Sarah Johnson',
    reviewDate: '2024-07-15',
    lastUpdated: '2024-07-15',
    categories: [
      { name: 'Technical Skills', score: 4.5, weight: 30, comments: 'Excellent problem-solving and coding abilities' },
      { name: 'Communication', score: 4.2, weight: 20, comments: 'Great at explaining complex concepts' },
      { name: 'Leadership', score: 4.0, weight: 25, comments: 'Shows good mentoring skills with junior developers' },
      { name: 'Innovation', score: 4.5, weight: 15, comments: 'Consistently brings creative solutions' },
      { name: 'Collaboration', score: 4.1, weight: 10, comments: 'Works well with cross-functional teams' }
    ],
    goals: [
      {
        id: 'g1',
        title: 'Lead platform migration project',
        description: 'Successfully migrate legacy systems to cloud infrastructure',
        status: 'achieved',
        rating: 5
      },
      {
        id: 'g2',
        title: 'Mentor junior developers',
        description: 'Provide guidance and support to 3 junior team members',
        status: 'achieved',
        rating: 4
      },
      {
        id: 'g3',
        title: 'Complete AWS certification',
        description: 'Obtain AWS Solutions Architect certification',
        status: 'partially-achieved',
        rating: 3
      }
    ],
    strengths: [
      'Exceptional technical expertise in modern web technologies',
      'Natural leadership qualities and mentoring abilities',
      'Proactive approach to problem-solving',
      'Strong communication skills across all levels'
    ],
    improvements: [
      'Could improve time management for multiple projects',
      'Would benefit from more involvement in architectural decisions'
    ],
    nextPeriodGoals: [
      'Complete AWS Solutions Architect certification',
      'Lead the new microservices architecture initiative',
      'Expand mentoring program to include cross-team collaboration'
    ]
  },
  {
    id: '2',
    employeeId: 'EMP002',
    employeeName: 'Sarah Williams',
    position: 'Product Manager',
    department: 'Product',
    reviewPeriod: {
      start: '2024-01-01',
      end: '2024-06-30'
    },
    status: 'in-progress',
    overallRating: 0,
    reviewerName: 'Michael Brown',
    reviewDate: '',
    lastUpdated: '2024-08-10',
    categories: [
      { name: 'Strategic Thinking', score: 0, weight: 25, comments: '' },
      { name: 'Stakeholder Management', score: 0, weight: 25, comments: '' },
      { name: 'Product Vision', score: 0, weight: 20, comments: '' },
      { name: 'Data Analysis', score: 0, weight: 15, comments: '' },
      { name: 'Team Collaboration', score: 0, weight: 15, comments: '' }
    ],
    goals: [
      {
        id: 'g4',
        title: 'Launch mobile app version 2.0',
        description: 'Successfully deliver the redesigned mobile application',
        status: 'achieved',
        rating: 5
      },
      {
        id: 'g5',
        title: 'Increase user engagement by 25%',
        description: 'Implement features to boost user engagement metrics',
        status: 'partially-achieved',
        rating: 3
      }
    ],
    strengths: [],
    improvements: [],
    nextPeriodGoals: []
  }
];

interface PerformanceMetrics {
  averageRating: number;
  reviewsCompleted: number;
  reviewsPending: number;
  reviewsOverdue: number;
  departmentRatings: { department: string; rating: number; count: number }[];
  topPerformers: { name: string; rating: number; department: string }[];
}

const mockMetrics: PerformanceMetrics = {
  averageRating: 4.1,
  reviewsCompleted: 45,
  reviewsPending: 12,
  reviewsOverdue: 3,
  departmentRatings: [
    { department: 'Engineering', rating: 4.3, count: 15 },
    { department: 'Product', rating: 4.0, count: 8 },
    { department: 'Sales', rating: 4.2, count: 12 },
    { department: 'Marketing', rating: 3.9, count: 6 },
    { department: 'HR', rating: 4.1, count: 4 }
  ],
  topPerformers: [
    { name: 'John Doe', rating: 4.8, department: 'Engineering' },
    { name: 'Alice Johnson', rating: 4.7, department: 'Sales' },
    { name: 'Bob Wilson', rating: 4.6, department: 'Product' },
    { name: 'Carol Davis', rating: 4.5, department: 'Marketing' }
  ]
};

export default function PerformanceManagement() {
  const [reviews, setReviews] = useState<PerformanceReview[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'draft' | 'in-progress' | 'completed' | 'overdue'>('all');
  const [selectedReview, setSelectedReview] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'reviews' | 'analytics' | 'goals'>('reviews');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setReviews(mockPerformanceReviews);
      setMetrics(mockMetrics);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredReviews = reviews.filter(review => {
    const matchesSearch = review.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      review.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      review.department.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || review.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'in-progress':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'draft':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      case 'overdue':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'in-progress':
        return <Clock className="h-4 w-4" />;
      case 'overdue':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const renderStarRating = (rating: number, size = 'small') => {
    const stars: React.ReactElement[] = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const starSize = size === 'small' ? 'h-4 w-4' : 'h-5 w-5';

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <Star key={i} className={`${starSize} fill-yellow-400 text-yellow-400`} />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <Star key={i} className={`${starSize} fill-yellow-400/50 text-yellow-400`} />
        );
      } else {
        stars.push(
          <Star key={i} className={`${starSize} text-gray-300 dark:text-gray-600`} />
        );
      }
    }

    return <div className="flex gap-1">{stars}</div>;
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
            <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-xl">
              <TrendingUp className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
            Performance Management
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Track and evaluate employee performance across your organization
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
            <Download className="h-4 w-4" />
            Export
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors">
            <Plus className="h-4 w-4" />
            New Review
          </button>
        </div>
      </div>

      {/* Metrics Dashboard */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Rating</p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">{metrics.averageRating}</p>
                  {renderStarRating(metrics.averageRating)}
                </div>
              </div>
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
                <Star className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-3xl font-bold text-green-600">{metrics.reviewsCompleted}</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending</p>
                <p className="text-3xl font-bold text-blue-600">{metrics.reviewsPending}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Overdue</p>
                <p className="text-3xl font-bold text-red-600">{metrics.reviewsOverdue}</p>
              </div>
              <div className="p-3 bg-red-100 dark:bg-red-900/20 rounded-lg">
                <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { key: 'reviews', label: 'Performance Reviews', icon: Award },
            { key: 'analytics', label: 'Analytics', icon: BarChart3 },
            { key: 'goals', label: 'Goals Tracking', icon: Target }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-orange-500 text-orange-600 dark:text-orange-400'
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
          {/* Reviews Tab */}
          {activeTab === 'reviews' && (
            <div className="space-y-6">
              {/* Search and Filters */}
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    type="text"
                    placeholder="Search reviews..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="in-progress">In Progress</option>
                  <option value="draft">Draft</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>

              {/* Reviews List */}
              <div className="space-y-4">
                {filteredReviews.map((review) => (
                  <div
                    key={review.id}
                    className="border border-gray-200 dark:border-gray-600 rounded-lg p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {review.employeeName}
                          </h3>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(review.status)}
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(review.status)}`}>
                              {review.status.replace('-', ' ').toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mb-1">{review.position} • {review.department}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          Review Period: {new Date(review.reviewPeriod.start).toLocaleDateString()} - {new Date(review.reviewPeriod.end).toLocaleDateString()}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          Reviewer: {review.reviewerName}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        {review.status === 'completed' && (
                          <div className="text-right">
                            <div className="flex items-center gap-2">
                              {renderStarRating(review.overallRating)}
                              <span className="text-lg font-bold text-gray-900 dark:text-white">
                                {review.overallRating}
                              </span>
                            </div>
                            <p className="text-sm text-gray-500 dark:text-gray-500">Overall Rating</p>
                          </div>
                        )}
                        
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
                    
                    {review.status === 'completed' && (
                      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Goals Achievement</h4>
                            <div className="space-y-1">
                              {review.goals.map(goal => (
                                <div key={goal.id} className="flex items-center justify-between text-sm">
                                  <span className="text-gray-600 dark:text-gray-400 truncate">{goal.title}</span>
                                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                    goal.status === 'achieved' ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' :
                                    goal.status === 'partially-achieved' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400' :
                                    'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                                  }`}>
                                    {goal.status === 'achieved' ? 'Achieved' : goal.status === 'partially-achieved' ? 'Partial' : 'Not Achieved'}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Top Categories</h4>
                            <div className="space-y-1">
                              {review.categories.slice(0, 3).map(category => (
                                <div key={category.name} className="flex items-center justify-between text-sm">
                                  <span className="text-gray-600 dark:text-gray-400">{category.name}</span>
                                  <span className="font-medium text-gray-900 dark:text-white">{category.score}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Review Date</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {new Date(review.reviewDate).toLocaleDateString()}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                              Last updated: {new Date(review.lastUpdated).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && metrics && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Department Ratings */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Department Performance</h3>
                  <div className="space-y-4">
                    {metrics.departmentRatings.map((dept, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">{dept.department}</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">{dept.count} employees</div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-2">
                            {renderStarRating(dept.rating)}
                            <span className="font-bold text-gray-900 dark:text-white">{dept.rating}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Performers */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Top Performers</h3>
                  <div className="space-y-4">
                    {metrics.topPerformers.map((performer, index) => (
                      <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                            #{index + 1}
                          </div>
                          <div>
                            <div className="font-semibold text-gray-900 dark:text-white">{performer.name}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{performer.department}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {renderStarRating(performer.rating)}
                          <span className="text-xl font-bold text-gray-900 dark:text-white">{performer.rating}</span>
                        </div>
                      </div>
                    ))}
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
