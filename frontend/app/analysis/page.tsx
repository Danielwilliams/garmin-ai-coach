'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AnalysisDashboard from '@/components/Analysis/AnalysisDashboard';
import { trainingProfileAPI } from '@/lib/api';

const AnalysisPage: React.FC = () => {
  const [trainingProfiles, setTrainingProfiles] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchTrainingProfiles();
  }, []);

  const fetchTrainingProfiles = async () => {
    try {
      const profiles = await trainingProfileAPI.getProfiles();
      setTrainingProfiles(profiles);
    } catch (error) {
      console.error('Failed to fetch training profiles:', error);
    } finally {
      setIsLoading(false);
    }
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
              <button
                onClick={() => router.push('/dashboard')}
                className="mr-4 text-gray-400 hover:text-gray-600"
              >
                ←
              </button>
              <h1 className="text-2xl font-bold text-gray-900">
                Training Analysis
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <AnalysisDashboard trainingProfiles={trainingProfiles} />
        </div>
      </main>
    </div>
  );
};

export default AnalysisPage;