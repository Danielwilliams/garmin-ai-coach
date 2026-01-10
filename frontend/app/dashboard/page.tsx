'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Button from '@/components/ui/Button';

const Dashboard: React.FC = () => {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    window.location.href = '/auth/login';
  };

  const handleCreateProfile = () => {
    router.push('/profile/create');
  };

  const handleStartAnalysis = () => {
    router.push('/analysis');
  };

  const handleViewProfiles = () => {
    router.push('/profile');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg
                  className="h-6 w-6 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h1 className="ml-3 text-2xl font-bold text-gray-900">
                Garmin AI Coach
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.full_name}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <div className="sm:flex sm:items-start sm:justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Welcome back, {user?.full_name}!
                  </h2>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    Your AI-powered triathlon coaching platform is ready to help you achieve your goals.
                  </p>
                </div>
                <div className="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0 sm:flex sm:items-center space-x-3">
                  <Button
                    variant="outline"
                    onClick={handleCreateProfile}
                  >
                    Create Profile
                  </Button>
                  <Button
                    onClick={handleStartAnalysis}
                  >
                    Start Analysis
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* User Info Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Account Information
              </h3>
              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Full name
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user?.full_name}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Email address
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user?.email}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Account status
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user?.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {user?.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Email verified
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user?.is_verified 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {user?.is_verified ? 'Verified' : 'Pending'}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <button className="relative rounded-lg border border-gray-300 bg-white px-6 py-4 shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <div>
                    <span className="block text-sm font-medium text-gray-900">
                      Connect Garmin
                    </span>
                    <span className="block text-sm text-gray-500">
                      Link your Garmin Connect account
                    </span>
                  </div>
                </button>

                <button 
                  onClick={handleCreateProfile}
                  className="relative rounded-lg border border-gray-300 bg-white px-6 py-4 shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <div>
                    <span className="block text-sm font-medium text-gray-900">
                      Create Training Profile
                    </span>
                    <span className="block text-sm text-gray-500">
                      Set up your training goals and competitions
                    </span>
                  </div>
                </button>

                <button 
                  onClick={handleViewProfiles}
                  className="relative rounded-lg border border-gray-300 bg-white px-6 py-4 shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <div>
                    <span className="block text-sm font-medium text-gray-900">
                      Manage Profiles
                    </span>
                    <span className="block text-sm text-gray-500">
                      View and edit your training profiles
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;